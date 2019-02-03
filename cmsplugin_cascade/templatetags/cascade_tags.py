# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import json
import os
from distutils.version import LooseVersion

from cms import __version__ as CMS_VERSION
from cms.toolbar.utils import get_toolbar_from_request
from django import template
from django.conf import settings
from django.core.cache import caches
from django.template.exceptions import TemplateDoesNotExist
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

from classytags.arguments import Argument
from classytags.core import Options, Tag

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
        from sekizai.helpers import get_varname
        from cmsplugin_cascade.strides import StrideContentRenderer

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
            varname = get_varname()
            SEKIZAI_CONTENT_HOLDER = cache.get_or_set(varname, context.get(varname))
            if SEKIZAI_CONTENT_HOLDER:
                for name in SEKIZAI_CONTENT_HOLDER:
                    context[varname][name] = SEKIZAI_CONTENT_HOLDER[name]
        return content

register.tag('render_cascade', StrideRenderer)


class RenderPlugin(Tag):
    name = 'render_plugin'
    options = Options(
        Argument('plugin')
    )

    def render_tag(self, context, plugin):
        if not plugin:
            return ''

        if LooseVersion(CMS_VERSION) < LooseVersion('3.5'):
            content_renderer = context['cms_content_renderer']
            content = content_renderer.render_plugin(
                instance=plugin,
                context=context,
                editable=content_renderer.user_is_on_edit_mode(),
            )
        else:
            toolbar = get_toolbar_from_request(context['request'])
            if 'cms_content_renderer' in context and context['cms_content_renderer'].__module__=="cmsplugin_cascade.strides" :
                content_renderer=context['cms_content_renderer']
            elif 'cms_renderer' in context.dicts[1]:
                content_renderer=context.dicts[1]['cms_renderer']
            elif  'cms_content_renderer' in context:
                content_renderer=context['cms_content_renderer']
            else:
                content_renderer = toolbar.content_renderer
            content = content_renderer.render_plugin(
                instance=plugin,
                context=context,
                editable=toolbar.edit_mode_active,
            )
        return content

register.tag('render_plugin', RenderPlugin)


@register.simple_tag
def sphinx_docs_include(path):
    filename = os.path.join(settings.SPHINX_DOCS_ROOT, path)
    if not os.path.exists(filename):
        raise TemplateDoesNotExist("'{path}' does not exist".format(path=path))
    with io.open(filename) as fh:
        return mark_safe(fh.read())
