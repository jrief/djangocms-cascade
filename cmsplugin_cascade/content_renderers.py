# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.loader import get_template
from django.utils.safestring import mark_safe

from classytags.utils import flatten_context
from cms.utils import get_language_from_request

from cmsplugin_cascade.plugin_base import readonly_plugins, readonly_elements


class CascadeContentRenderer(object):
    def __init__(self, request):
        self.request = request
        self.language = get_language_from_request(request)
        self._cached_templates = {}

    def render_tree(self, context, tree_data):
        content = []
        for plugin_type, data, children_data in tree_data['plugins']:
            plugin_class = readonly_plugins.get(plugin_type)
            element_class = readonly_elements.get(plugin_type)
            plugin_instance = element_class(plugin_class(), data.get('glossary', {}), children_data)
            content.append(self.render_plugin(plugin_instance, context))
        return mark_safe(''.join(content))

    def render_plugin(self, instance, context, placeholder=None, editable=False):
        # context = PluginContext(context, instance, placeholder)
        context = instance.plugin.render(context, instance, placeholder)
        context = flatten_context(context)

        template = instance.plugin._get_render_template(context, instance, placeholder)
        template = self.get_cached_template(template)
        content = template.render(context)
        return content

    def user_is_on_edit_mode(self):
        return False

    def get_cached_template(self, template):
        if hasattr(template, 'render'):
            return template

        if not template in self._cached_templates:
            self._cached_templates[template] = get_template(template)
        return self._cached_templates[template]
