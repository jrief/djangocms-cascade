import io
import json
import os
import random
from cms.toolbar.utils import get_toolbar_from_request
from django import template
from django.conf import settings
from django.core.cache import caches
from django.template.exceptions import TemplateDoesNotExist
from django.templatetags.static import static
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from classytags.arguments import Argument
from classytags.core import Options, Tag
from cmsplugin_cascade.strides import StrideContentRenderer

register = template.Library()


class StrideRenderer(Tag):
    """
    Render the serialized content of a placeholder field using the full cascade of plugins.
    {% render_cascade "cascade-data.json" %}

    Keyword arguments:
    datafile -- Filename containing the cascade tree. Must be file locatable by Django's
    static file finders.
    """
    name = 'render_cascade'
    options = Options(
        Argument('datafile'),
    )

    def render_tag(self, context, datafile):
        from sekizai.helpers import get_varname as get_sekizai_context_key
        from cmsplugin_cascade.strides import StrideContentRenderer

        cache = caches['default']
        tree_data_key = 'cascade-strides:' + datafile
        tree_data = cache.get(tree_data_key) if cache else None
        if tree_data is None:
            jsonfile = finders.find(datafile)
            if not jsonfile:
                raise IOError("Unable to find file: {}".format(datafile))

            with io.open(jsonfile) as fp:
                tree_data = json.load(fp)

        content_renderer = StrideContentRenderer(context['request'])
        with context.push(cms_content_renderer=content_renderer):
            content = content_renderer.render_cascade(context, tree_data)

        # some templates use Sekizai's templatetag `addtoblock` or `add_data`, which have to be re-added to the context
        cache = caches['default']
        if cache:
            sekizai_context_key = get_sekizai_context_key()
            SEKIZAI_CONTENT_HOLDER = cache.get_or_set(sekizai_context_key, context.get(sekizai_context_key))
            if SEKIZAI_CONTENT_HOLDER:
                for name in SEKIZAI_CONTENT_HOLDER:
                    context[sekizai_context_key][name] = SEKIZAI_CONTENT_HOLDER[name]
        return content

register.tag('render_cascade', StrideRenderer)


class RenderPlugin(Tag):
    """
    Alternative implementation of django-CMS's templatetag ``render_plugin``.
    It can either handle normal CMS plugins or Strides.
    """
    name = 'render_plugin'
    options = Options(
        Argument('plugin')
    )

    def render_tag(self, context, plugin):
        if not plugin:
            return ''

        request = context['request']
        toolbar = get_toolbar_from_request(request)
        if 'cms_content_renderer' in context and isinstance(context['cms_content_renderer'], StrideContentRenderer):
            content_renderer = context['cms_content_renderer']
        elif 'cms_renderer' in context:
            content_renderer = context['cms_renderer']
        elif 'cms_content_renderer' in context:
            content_renderer = context['cms_content_renderer']
        else:
            content_renderer = toolbar.content_renderer
        content = content_renderer.render_plugin(
            instance=plugin,
            context=context,
            editable=toolbar.edit_mode_active,
        )
        return content

register.tag('render_plugin', RenderPlugin)


@register.filter
def is_valid_image(image):
    try:
        return image.file.file
    except:
        return False


class FallBack(Tag):
    name = 'fallback'

    options = Options(
        Argument('plugin',required=False) 
    )
    
    def render_tag(self, context, plugin):
        for context_ in  context:
           if 'instance'in context_ :
               glossary = context_['instance'].glossary
               instance = context_['instance']
               fallback_plugin_type = plugin.plugin_class.__name__
               css_classes = glossary.get('css_classes','')
               width = 0; height = 0; exif_orientation = 0; x = 0; y = 0;
               inline_styles = glossary.get('inline_styles','')
               html_tag_attributes = glossary.get('html_tag_attributes','')

               if 'image' in glossary:
                   image_fallback='image'
                   static_fallback_svg = static('cascade/fallback_light.svg')
                   # color skybkue
                   svg_color = 'hsl(196, 71%, 93%, 0.8)'
                   
               elif fallback_plugin_type == 'BootstrapJumbotronPlugin':
                   image_fallback=None
                   static_fallback_svg = static('cascade/fallback_light_jumbotron.svg')
                   # color morning
                   svg_color = 'hsl(62, 90%, 90%, 0.8)'            
               elif '_image_properties' in  glossary:
                   image_fallback='_image_properties'
                   ramdom_svg_color = 'hsl(368, 80%,95%, 0.8)'
                   static_fallback_svg = static('cascade/fallback_light_picture.svg')
                   # color sunrise
                   svg_color = 'hsl(368, 80%,95%, 0.8)'             
               else:
                   image_fallback=None
                   static_fallback_svg = static('cascade/fallback_light_picture.svg')
                   # color garden
                   svg_color = 'hsl(150, 86%,94%, 0.8)'
               if image_fallback :
                   width = glossary[image_fallback].get('width',0)
                   height = glossary[image_fallback].get('height',0)
                   exif_orientation = glossary[image_fallback].get('exif_orientation',0) 
               if width >= 1:
                   x = random.randint(0,round(width/1.19))
               if height >= 1:                  
                   y = random.randint(0,round(height/1.19))
 
               if fallback_plugin_type == 'BootstrapJumbotronPlugin':
                   style='''
                        background: url({static_fallback_svg});
                        background-size: auto;
                        background-position-y: 20%;
                        background-size: 50%;
                        background-repeat: no-repeat;
                        background-position-x: 50%;
                        background-attachment: fixed;
                        background-color: {svg_color};
                        border: white solid;
                    '''.format( ramdom_svg_color=svg_color, static_fallback_svg=static_fallback_svg)
                    
                   return style
               else:
                   svg='<svg  ViewBox="0 0 {width} {height}" version="1.1" style="background-color:\
                    {svg_color}; border: white solid;" {html_tag_attributes} class="{css_classes}"   style="{inline_styles}" \
                    xmlns="http://www.w3.org/2000/svg" xmlns:xlink= "http://www.w3.org/1999/xlink"> \
                    <image x="{x}"  y="{y}" width="10%" xlink:href="{static_fallback_svg}"> \
                    </svg>'.format(
                    width=width,
                    height=height,
                    svg_color=svg_color,
                    css_classes=css_classes,
                    inline_styles=inline_styles,
                    html_tag_attributes=html_tag_attributes,
                    static_fallback_svg=static_fallback_svg,
                    x=x,
                    y=y)
                   return svg
                
register.tag('fallback', FallBack)

@register.simple_tag
def sphinx_docs_include(path):
    filename = os.path.join(settings.SPHINX_DOCS_ROOT, path)
    if not os.path.exists(filename):
        raise TemplateDoesNotExist("'{path}' does not exist".format(path=path))
    with io.open(filename) as fh:
        return mark_safe(fh.read())
