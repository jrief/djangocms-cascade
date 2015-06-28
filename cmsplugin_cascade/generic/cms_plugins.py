# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
