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
        Argument('data_clipboard'),
        Argument('identifier', required=True),
    )

    def render_tag(self, context, data_clipboard, identifier=None):
        from sekizai.helpers import get_varname as get_sekizai_context_key
        from cmsplugin_cascade.strides import StrideContentRenderer

        if isinstance(data_clipboard, dict):
            identifier = identifier
            datafile = False
        else :
            datafile = data_clipboard
            identifier = datafile
        tree_data_key = 'cascade-strides:' + identifier
        cache = caches['default']
        tree_data = cache.get(tree_data_key) if cache else None
        if tree_data is None:
            if datafile:
                jsonfile = finders.find(datafile)
                if not jsonfile:
                    raise IOError("Unable to find file: {}".format(datafile))
                    with io.open(jsonfile) as fp:
                        tree_data = json.load(fp)
                else:
                    tree_data = json.load(data_clipboard)
            else:
                tree_data = data_clipboard
        if 'request' in context:
            data_req = context['request']
        else:
            data_req = None
        content_renderer = StrideContentRenderer(data_req)
        with context.push(cms_content_renderer=content_renderer):
            content = content_renderer.render_cascade(context, tree_data)

        # some templates use Sekizai's templatetag `addtoblock` or `add_data`, which have to be re-added to the context
        cache = caches['default']
        if cache:
            sekizai_context_key = get_sekizai_context_key()
            SEKIZAI_CONTENT_HOLDER = cache.get_or_set(sekizai_context_key, context.get(sekizai_context_key))
            if SEKIZAI_CONTENT_HOLDER:
                for name in SEKIZAI_CONTENT_HOLDER:
                    context[sekizai_context_key] = {'name':''}
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
