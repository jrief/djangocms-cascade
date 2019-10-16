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
        Argument('plugin',required=False, default='world') 
    )
    
    def render_tag(self, context, plugin):
        for context_ in  context:
           if 'instance'in context_ :
               glossary = context_['instance'].glossary
               plugin_type = context_['instance'].plugin_type
               if plugin_type == 'BootstrapImagePlugin':
                   ramdom_svg_color = 'hsl({}, 30%, 80%, 0.8)'.format( str(random.randint(800, 900)))
                   image_fallback='image'
               if plugin_type == 'BootstrapPicturePlugin':
                   ramdom_svg_color = 'hsl({}, 30%, 80%, 0.8)'.format( str(random.randint(0, 100)))
                   image_fallback='_image_properties'
               if plugin_type == 'BootstrapJumbotronPlugin':
                   ramdom_svg_color = 'hsl({}, 30%, 80%, 0.8)'.format( str(random.randint(400, 500)))
                   image_fallback='_image_properties'
                
               witdh = glossary[image_fallback].get('width','')
               height = glossary[image_fallback].get('height','')
               exif_orientation = glossary[image_fallback].get('exif_orientation','') 
               css_classes =   glossary.get('css_classes','') 
               inline_styles =  glossary.get('inline_styles', '')
               html_tag_attributes =  glossary.get('html_tag_attributes','')
               static_fallback_svg = static('cascade/fallback_light.svg')
               x = random.randint(0,round(witdh/1.19))
               y = random.randint(0,round(height/1.19))
            
               svg='<svg  class="mx-auto" ViewBox="0 0 {witdh} {height}" version="1.1" style="background-color:\
                {ramdom_svg_color};" {html_tag_attributes} class="{css_classes}"   style="{inline_styles}" \
                xmlns="http://www.w3.org/2000/svg" xmlns:xlink= "http://www.w3.org/1999/xlink"> \
                <image x="{x}"  y="{y}"  width="10%" xlink:href="{static_fallback_svg}"> \
                </svg>'.format(
                    witdh=witdh,
                    height=height,
                    ramdom_svg_color=ramdom_svg_color,
                    css_classes=css_classes,
                    inline_styles = inline_styles,
                    html_tag_attributes = html_tag_attributes,
                    static_fallback_svg=static_fallback_svg,
                    x=x,
                    y=y)
               return mark_safe(svg)

register.tag('fallback', FallBack)

@register.simple_tag
def sphinx_docs_include(path):
    filename = os.path.join(settings.SPHINX_DOCS_ROOT, path)
    if not os.path.exists(filename):
        raise TemplateDoesNotExist("'{path}' does not exist".format(path=path))
    with io.open(filename) as fh:
        return mark_safe(fh.read())
