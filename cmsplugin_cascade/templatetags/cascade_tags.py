# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import template
from django.core.cache import caches
from django.template.exceptions import TemplateSyntaxError
from django.contrib.staticfiles import finders

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

        with open(jsonfile) as fp:
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
            raise TemplateSyntaxError("Plugin is missing")

        content_renderer = context['cms_content_renderer']
        content = content_renderer.render_plugin(
            instance=plugin,
            context=context,
            editable=content_renderer.user_is_on_edit_mode(),
        )
        return content

register.tag('render_plugin', RenderPlugin)
