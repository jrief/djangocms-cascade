import io
import json

from django import template
from django.core.cache import caches
from django.contrib.staticfiles import finders
from django.urls import NoReverseMatch

from cms.cache.page import get_page_url_cache, set_page_url_cache
from cms.templatetags.cms_tags import PageUrl as BasePageUrl, _get_page_by_untyped_arg
from cms.toolbar.utils import get_toolbar_from_request
from cms.plugin_rendering import StructureRenderer
from cms.utils import get_current_site, get_language_from_request
from cms.utils.conf import get_site_id

from classytags.arguments import Argument, MultiKeywordArgument
from classytags.core import Options, Tag

from cmsplugin_cascade.models import PageAnchor
from cmsplugin_cascade.strides import StrideContentRenderer


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


class RenderPlugin(Tag):
    """
    Alternative implementation of django-CMS's templatetag ``render_plugin``.
    It can either handle normal CMS plugins or Strides.
    """
    name = 'render_plugin'
    options = Options(
        Argument('plugin'),
        MultiKeywordArgument('kwargs', required=False, default={}),
    )

    def render_tag(self, context, plugin, kwargs):
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
        if isinstance(content_renderer, StructureRenderer):
            return content_renderer.render_plugin(plugin)
        else:
            context.update(kwargs)
            return content_renderer.render_plugin(
                instance=plugin,
                context=context,
                editable=toolbar.edit_mode_active,
            )


class PageUrl(BasePageUrl):
    options = Options(
        Argument('page_lookup'),
        Argument('anchor'),
        Argument('lang', required=False, default=None),
        Argument('site', required=False, default=None),
        "as",
        Argument('varname', required=False, resolve=False),
    )

    def get_value(self, context, page_lookup, anchor, lang, site):
        if isinstance(page_lookup, str) and page_lookup.isnumeric():
            page_lookup = int(page_lookup)
        if isinstance(anchor, str) and anchor.isnumeric():
            anchor = int(anchor)
        elif not isinstance(anchor, int):
            anchor = None

        request = context.get('request', False)
        if not request:
            return ""
        if lang is None:
            lang = get_language_from_request(request)
        site_id = get_site_id(site) if site else get_current_site(request).pk

        if page := _get_page_by_untyped_arg(page_lookup, request, site_id):
            try:
                url = page.get_absolute_url(language=lang)
                if not url:
                    return ""  # Return empty string if Title object is missing
                # set_page_url_cache(page_lookup, lang, site_id, url)
            except NoReverseMatch:
                return ""  # Suppress NoReverseMatch error
            else:
                page_url = page.get_url_obj(language=lang)
                try:
                    url += f'#{page_url.anchors.get(id=anchor).identifier}'
                except (PageAnchor.DoesNotExist, ValueError):
                    pass
                return url
        return ""


register = template.Library()
register.tag('render_plugin', RenderPlugin)
register.tag('page_url', PageUrl)
register.tag('render_cascade', StrideRenderer)
