# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.forms import widgets
from django.http.response import HttpResponse, JsonResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase, TransparentContainer
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.widgets import CascadingSizeWidget, SetBorderWidget, ColorPickerWidget


class SimpleWrapperPlugin(TransparentContainer, CascadePluginBase):
    name = _("Simple Wrapper")
    parent_classes = None
    require_parent = False
    allow_children = True
    alien_child_classes = True
    TAG_CHOICES = tuple((cls, _("<{}> – Element").format(cls))
        for cls in ('div', 'span', 'section', 'article',)) + (('naked', _("Naked Wrapper")),)

    tag_type = GlossaryField(
        widgets.Select(choices=TAG_CHOICES),
        label=_("HTML element tag"),
        help_text=_('Choose a tag type for this HTML element.')
    )

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(SimpleWrapperPlugin, cls).get_identifier(instance)
        tag_name = dict(cls.TAG_CHOICES).get(instance.glossary.get('tag_type'))
        if tag_name:
            return format_html('{0} {1}', tag_name, identifier)
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
    TAG_TYPES = tuple(('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7))

    tag_type = GlossaryField(widgets.Select(choices=TAG_TYPES))

    content = GlossaryField(
        widgets.TextInput(attrs={'style': 'width: 350px; font-weight: bold; font-size: 125%;'}),
         _("Heading content"))

    render_template = 'cascade/generic/heading.html'

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css',)}

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(HeadingPlugin, cls).get_identifier(instance)
        tag_type = instance.glossary.get('tag_type')
        content = instance.glossary.get('content')
        if tag_type:
            return format_html('<code>{0}</code>: {1} {2}', tag_type, content, identifier)
        return content

plugin_pool.register_plugin(HeadingPlugin)


class CustomSnippetPlugin(TransparentContainer, CascadePluginBase):
    """
    Allows to add a customized template anywhere. This plugins will be registered only if the
    project added a template using the configuration setting 'plugins_with_extra_render_templates'.
    """
    name = _("Custom Snippet")
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
    # register only, if at least one template has been defined
    plugin_pool.register_plugin(CustomSnippetPlugin)
