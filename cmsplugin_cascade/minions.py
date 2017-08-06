# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from classytags.utils import flatten_context
from cms.utils import get_language_from_request
from djangocms_text_ckeditor.utils import OBJ_ADMIN_RE


__all__ = ['register_minion', 'MinionContentRenderer']

class EmulateQuerySet(object):
    def __init__(self, elements):
        self.elements = elements

    def all(self):
        for e in self.elements:
            yield type(str('MinionInlineElement'), (object,), {'glossary': e})()


class MinionElementBase(object):
    """
    Emulate a CascadeElement to be used by the CascadeContentRenderer instead of the CMSContentRenderer.
    """
    def __init__(self, plugin, data, children_data, parent=None):
        self.plugin = plugin
        self.pk = data.get('pk')
        self.glossary = data.get('glossary', {})
        self.sortinline_elements = self.inline_elements = EmulateQuerySet(data.get('inlines', []))
        self.children_data = children_data
        self.parent = parent

    @property
    def plugin_class(self):
        return self.plugin.__class__

    def child_plugin_instances(self):
        for plugin_type, data, children_data in self.children_data:
            plugin_class = _minion_plugin_map.get(plugin_type)
            element_class = _minion_element_map.get(plugin_type)
            if element_class:
                yield element_class(plugin_class(), data, children_data, parent=self)

    def get_complete_glossary(self):
        if not hasattr(self, '_complete_glossary_cache'):
            self._complete_glossary_cache = self.get_parent_glossary().copy()
            self._complete_glossary_cache.update(self.glossary or {})
        return self._complete_glossary_cache

    def get_parent_glossary(self):
        if self.parent:
            return self.parent.get_complete_glossary()
        return {}
        # TODO: use self.placeholder.glossary as the starting dictionary
        template = self.placeholder.page.template if self.placeholder.page else None
        return get_placeholder_conf('glossary', self.placeholder.slot, template=template, default={})

    @property
    def tag_type(self):
        return self.plugin_class.get_tag_type(self)

    @property
    def css_classes(self):
        css_classes = self.plugin_class.get_css_classes(self)
        return mark_safe(' '.join(c for c in css_classes if c))

    @property
    def inline_styles(self):
        inline_styles = self.plugin_class.get_inline_styles(self)
        return format_html_join(' ', '{0}: {1};', (s for s in inline_styles.items() if s[1]))

    @property
    def html_tag_attributes(self):
        attributes = self.plugin_class.get_html_tag_attributes(self)
        return format_html_join(' ', '{0}="{1}"', ((attr, val) for attr, val in attributes.items() if val))


class TextMinionElement(object):
    def __init__(self, plugin, data, children_data, parent=None):
        self.plugin = plugin
        self.pk = data.get('pk')
        self.body = data.get('body')
        self.children_data = children_data
        self.parent = parent

    def tags_to_user_html(self, context, placeholder):
        content_renderer = context['cms_content_renderer']
        children_instances = {}
        for plugin_type, data, children_data in self.children_data:
            plugin_class = _minion_plugin_map.get(plugin_type)
            element_class = _minion_element_map.get(plugin_type)
            if element_class and 'pk' in data:
                sub_plugin = plugin_class()
                children_instances[data['pk']] = element_class(sub_plugin, data, children_data, parent=self)

        def _render_tag(m):
            plugin_id = int(m.groupdict()['pk'])
            instance = children_instances[plugin_id]
            with context.push():
                sub_context = instance.plugin.render(context, instance, placeholder)
                return content_renderer.render_plugin(instance, sub_context)

        return OBJ_ADMIN_RE.sub(_render_tag, self.body)


class MinionPluginBase(object):
    """
    Whenever djangocms-cascade is used in readonly mode, all Cascade plugins are instantiated a second time
    where class CascadePluginBase is replaced against this class in order to remove its dependency to django-CMS.
    """
    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
        })
        return context

    def _get_render_template(self, context, instance, placeholder):
        if hasattr(self, 'get_render_template'):
            template = self.get_render_template(context, instance, placeholder)
        elif getattr(self, 'render_template', False):
            template = getattr(self, 'render_template', False)
        else:
            template = None

        if not template:
            raise TemplateDoesNotExist("plugin {} has no render_template".format(self.__class__))
        return template


class TextMinionPlugin(MinionPluginBase):
    render_template = 'cms/plugins/text.html'

    def render(self, context, instance, placeholder):
        context.update({
            'body': instance.tags_to_user_html(context, placeholder),
        })
        return context


class MinionContentRenderer(object):
    def __init__(self, request):
        self.request = request
        self.language = get_language_from_request(request)
        self._cached_templates = {}

    def render_tree(self, context, tree_data):
        content = []
        for plugin_type, data, children_data in tree_data['plugins']:
            plugin_class = _minion_plugin_map.get(plugin_type)
            element_class = _minion_element_map.get(plugin_type)
            plugin_instance = element_class(plugin_class(), data, children_data)
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


def register_minion(name, bases, attrs, model_mixins):
    # create a fake plugin class
    plugin_bases = tuple(_minion_plugin_map.get(b.__name__, b) for b in bases)
    if name == 'CascadePluginBase':
        # interrupt MRO: replace methods from CMSPluginBase by MinionPluginBase's
        for key, val in attrs.items():
            if hasattr(MinionPluginBase, key):
                attrs.pop(key)
        _minion_plugin_map[name] = type(str('MinionPluginBase'), plugin_bases, attrs)
    else:
        _minion_plugin_map[name] = type(name, plugin_bases, attrs)

        # create a corresponding minion element class
        element_bases = model_mixins + (MinionElementBase,)
        _minion_element_map[name] = type(str(name + 'Element'), element_bases, {})


_minion_plugin_map = {
    'CMSPluginBase': MinionPluginBase,
    'TextPlugin': TextMinionPlugin,
}
_minion_element_map = {
    'TextPlugin': TextMinionElement,
}
