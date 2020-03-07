import io
import json
import os
from cms.toolbar.utils import get_toolbar_from_request
from django import template
from django.conf import settings
from django.core.cache import caches
from django.template.exceptions import TemplateDoesNotExist
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from classytags.arguments import Argument
from classytags.core import Options, Tag
from cmsplugin_cascade.strides import StrideContentRenderer
from django.templatetags.static import static

register = template.Library()


class StrideRenderer(Tag):
    """
    Render the serialized content of a placeholder field using the full cascade of plugins.
    {% render_cascade "cascade-data.json" %}

    Keyword arguments:
    data_clipboard -- Filename containing the cascade tree. Must be file locatable by Django's
    static file finders.
    identifier --- Identifier persitent clipboard db.
    """
    name = 'render_cascade'
    options = Options(
        Argument('data_clipboard'),
        Argument('identifier', required=False),
    )

    def render_tag(self, context, data_clipboard, identifier=None):
        from sekizai.helpers import get_varname as get_sekizai_context_key
        from cmsplugin_cascade.strides import StrideContentRenderer

        if isinstance(data_clipboard, dict):
            # qs_clipboards
            identifier = identifier
            datafile = False
        elif isinstance(data_clipboard, str):
            # relative path
            datafile = data_clipboard
            identifier = datafile

        tree_data_key = 'cascade-strides:' + identifier
        cache = caches['default']
        tree_data = cache.get(tree_data_key) if cache else None

        if tree_data is None:
            if datafile :
                jsonfile = finders.find(datafile)
                if not jsonfile:
                    raise IOError("Unable to find file: {}".format(datafile))
                with io.open(jsonfile) as fp:
                    tree_data = json.load(fp)
            else:
                tree_data = data_clipboard
        request = context['request']
        content_renderer = StrideContentRenderer(request)
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
        if 'cms_content_renderer' in context and isinstance(context['cms_content_renderer'], StrideContentRenderer):
            content_renderer = context['cms_content_renderer']
        elif 'cms_renderer' in context:
            content_renderer = context['cms_renderer']
        elif 'cms_content_renderer' in context:
            content_renderer = context['cms_content_renderer']
        else:
            request = context['request']
            toolbar = get_toolbar_from_request(request)
            content_renderer = toolbar.content_renderer
        try:
           toolbar_edit_mode = toolbar.edit_mode_active
        except UnboundLocalError:
           toolbar_edit_mode = True
        content = content_renderer.render_plugin(
            instance=plugin,
            context=context,
            editable=toolbar_edit_mode
        )
        return content

register.tag('render_plugin', RenderPlugin)


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
                   image_fallback = 'image'
                   img = settings.CMSPLUGIN_CASCADE["fallback"]["image"]['svg']
                   color = settings.CMSPLUGIN_CASCADE["fallback"]["image"]['color']
                   static_fallback_svg = static(img)
               elif fallback_plugin_type == 'BootstrapJumbotronPlugin':
                   image_fallback=None
                   img = settings.CMSPLUGIN_CASCADE["fallback"]["jumbotron"]['svg']
                   color = settings.CMSPLUGIN_CASCADE["fallback"]["jumbotron"]['color']
                   static_fallback_svg = static(img)
               elif 'image_properties' in  glossary:
                   image_fallback='image_properties'
                   img = settings.CMSPLUGIN_CASCADE["fallback"]["picture"]['svg']
                   color = settings.CMSPLUGIN_CASCADE["fallback"]["picture"]['color']
                   static_fallback_svg = static(img)
               else:
                   image_fallback=None
                   img = settings.CMSPLUGIN_CASCADE["fallback"]["picture"]['svg']
                   color = settings.CMSPLUGIN_CASCADE["fallback"]["picture"]['color']
                   static_fallback_svg = static(img)
               if image_fallback :
                   width = glossary[image_fallback].get('width',0)
                   height = glossary[image_fallback].get('height',0)
                   exif_orientation = glossary[image_fallback].get('exif_orientation',0) 

               x = 50
               y = 50

               if fallback_plugin_type == 'BootstrapJumbotronPlugin':
                   style='''
                        background: url({static_fallback_svg});
                        background-size: auto;
                        background-position-y: 20%;
                        background-size: 50%;
                        background-repeat: no-repeat;
                        background-position-x: 50%;
                        background-attachment: fixed;
                        background-color: {color};
                        border: white solid;
                    '''.format( color=color, static_fallback_svg=static_fallback_svg)

                   return style
               else:
                   svg='<svg  ViewBox="0 0 {width} {height}" version="1.1" style="background-color:\
                    {color}; border: white solid;" {html_tag_attributes} class="{css_classes}"   style="{inline_styles}" \
                    xmlns="http://www.w3.org/2000/svg" xmlns:xlink= "http://www.w3.org/1999/xlink"> \
                    <image x="{x}"  y="{y}" width="10%" xlink:href="{static_fallback_svg}"> \
                    </svg>'.format(
                    width=width,
                    height=height,
                    color=color,
                    css_classes=css_classes,
                    inline_styles=inline_styles,
                    html_tag_attributes=html_tag_attributes,
                    static_fallback_svg=static_fallback_svg,
                    x=x,
                    y=y)
                   return svg

register.tag('fallback', FallBack)

@register.filter
def is_valid_image(image):
    try:
        return image.file.file
    except:
        return False


@register.simple_tag
def sphinx_docs_include(path):
    filename = os.path.join(settings.SPHINX_DOCS_ROOT, path)
    if not os.path.exists(filename):
        raise TemplateDoesNotExist("'{path}' does not exist".format(path=path))
    with io.open(filename) as fh:
        return mark_safe(fh.read())


@register.simple_tag
def cascadeclipboard_data_by_identifier(queryset, identifier ):
    qs_identifier=queryset.filter(identifier=identifier)
    return qs_identifier[0].data

@register.simple_tag
def fallback_config(type_fallback):
    return settings.CMSPLUGIN_CASCADE["fallback"][type_fallback]
