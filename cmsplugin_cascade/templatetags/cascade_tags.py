# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import template
from django.template.exceptions import TemplateSyntaxError
from django.contrib.staticfiles import finders

from classytags.arguments import Argument
from classytags.core import Options, Tag

register = template.Library()


class MinionRenderer(Tag):
    """
    {% render_tree "tree-data.json" %}

    Keyword arguments:
    datafile -- Filename containing the tree data. Must be findable
    """
    name = 'render_tree'
    options = Options(
        Argument('datafile'),
    )

    def render_tag(self, context, datafile):
        from cmsplugin_cascade.minions import MinionContentRenderer

        jsonfile = finders.find(datafile)
        if not jsonfile:
            raise IOError("Unable to find file: {}".format(datafile))

        with open(jsonfile) as fp:
            tree_data = json.load(fp)

        content_renderer = MinionContentRenderer(context['request'])
        with context.push(cms_content_renderer=content_renderer):
            content = content_renderer.render_tree(context, tree_data)
        return content

register.tag('render_tree', MinionRenderer)


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
