# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from .plugin_base import BootstrapPluginBase
from . import settings


class SimpleWrapperPlugin(BootstrapPluginBase):
    name = _("Simple Wrapper")
    parent_classes = ['BootstrapColumnPlugin']
    generic_child_classes = settings.CASCADE_LEAF_PLUGINS
    TAG_CHOICES = tuple((cls, cls.title()) for cls in ('div', 'span', 'section', 'article',))
    glossary_fields = (
        PartialFormField('element_tag',
            widgets.Select(choices=TAG_CHOICES),
            label=_("HTML element tag"),
            help_text=_('Choose a tag type for this HTML element.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(SimpleWrapperPlugin, cls).get_identifier(obj)
        tag = obj.glossary.get('element_tag', cls.TAG_CHOICES[0][1])
        return format_html('{0}{1}', identifier, tag.title())

plugin_pool.register_plugin(SimpleWrapperPlugin)


class HorizontalRulePlugin(BootstrapPluginBase):
    name = _("Horizontal Rule")
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    allow_children = False
    tag_type = 'hr'
    render_template = 'cms/plugins/single.html'
    glossary_fields = ()

plugin_pool.register_plugin(HorizontalRulePlugin)
