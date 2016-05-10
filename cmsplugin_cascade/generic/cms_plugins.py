# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.forms import widgets
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.mixins import TransparentMixin


class SimpleWrapperPlugin(TransparentMixin, CascadePluginBase):
    name = _("Simple Wrapper")
    parent_classes = None
    require_parent = False
    allow_children = True
    alien_child_classes = True
    TAG_CHOICES = tuple((cls, _("<{}> – Element").format(cls))
        for cls in ('div', 'span', 'section', 'article',)) + (('naked', _("Naked Wrapper")),)
    glossary_fields = (
        PartialFormField('tag_type',
            widgets.Select(choices=TAG_CHOICES),
            label=_("HTML element tag"),
            help_text=_('Choose a tag type for this HTML element.')
        ),
    )

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(SimpleWrapperPlugin, cls).get_identifier(instance)
        tag_name = dict(cls.TAG_CHOICES).get(instance.glossary.get('tag_type'))
        if tag_name:
            return format_html('{0}{1}', identifier, tag_name)
        return identifier

    def get_render_template(self, context, instance, placeholder):
        if instance.glossary.get('tag_type') == 'naked':
            return 'cascade/generic/naked.html'
        return 'cascade/generic/wrapper.html'

plugin_pool.register_plugin(SimpleWrapperPlugin)


class HorizontalRulePlugin(CascadePluginBase):
    name = _("Horizontal Rule")
    parent_classes = None
    allow_children = False
    tag_type = 'hr'
    render_template = 'cascade/generic/single.html'
    glossary_fields = ()

plugin_pool.register_plugin(HorizontalRulePlugin)


class HeadingPlugin(CascadePluginBase):
    name = _("Heading")
    parent_classes = None
    allow_children = False
    TAG_CHOICES = tuple((k, _("Heading {}").format(k)) for k in range(1, 7))
    glossary_fields = (
        PartialFormField('head_size',
            widgets.Select(choices=TAG_CHOICES)),
        PartialFormField('content',
            widgets.TextInput(attrs={'style': 'width: 350px;'}),
             _("Heading content")),
    )
    render_template = 'cascade/generic/heading.html'

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css',)}

    @classmethod
    def get_identifier(cls, instance):
        head_size = instance.glossary.get('head_size')
        content = instance.glossary.get('content')
        if head_size:
            return format_html('<strong>{0}</strong>: {1}', head_size, content)
        return content

    def render(self, context, instance, placeholder):
        context = super(HeadingPlugin, self).render(context, instance, placeholder)
        context['glossary'] = instance.glossary
        return context

plugin_pool.register_plugin(HeadingPlugin)


class CustomSnippetPlugin(TransparentMixin, CascadePluginBase):
    """
    Allows to add a customized template anywhere. This plugins will be registered only if the
    project added a template using the configuration setting 'plugins_with_extra_render_templates'.
    """
    name = _("Custom Snippet")
    parent_classes = None
    require_parent = False
    allow_children = True
    alien_child_classes = True
    render_template_choices = dict(settings.CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].get('CustomSnippetPlugin', ()))
    render_template = 'cascade/generic/does_not_exist.html'  # default in case the template could not be found

    @classmethod
    def get_identifier(cls, instance):
        render_template = instance.glossary.get('render_template')
        if render_template:
            return format_html('{}', cls.render_template_choices.get(render_template))

if CustomSnippetPlugin.render_template_choices:
    plugin_pool.register_plugin(CustomSnippetPlugin)
