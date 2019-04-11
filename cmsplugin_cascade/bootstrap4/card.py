# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import TransparentContainer, TransparentWrapper
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase


class CardChildBase(BootstrapPluginBase):
    require_parent = True
    parent_classes = ['BootstrapCardPlugin']
    allow_children = True
    render_template = 'cascade/generic/wrapper.html'
    child_classes = ['BootstrapCardHeaderPlugin', 'BootstrapCardBodyPlugin', 'BootstrapCardFooterPlugin']


class BootstrapCardHeaderPlugin(TransparentContainer, CardChildBase):
    name = _("Card Header")
    default_css_class = 'card-header'

plugin_pool.register_plugin(BootstrapCardHeaderPlugin)


class BootstrapCardBodyPlugin(TransparentContainer, CardChildBase):
    name = _("Card Body")
    default_css_class = 'card-body'

plugin_pool.register_plugin(BootstrapCardBodyPlugin)


class BootstrapCardFooterPlugin(TransparentContainer, CardChildBase):
    name = _("Card Footer")
    default_css_class = 'card-footer'

plugin_pool.register_plugin(BootstrapCardFooterPlugin)


class BootstrapCardPlugin(TransparentWrapper, BootstrapPluginBase):
    """
    Use this plugin to display a card with optional card-header and card-footer.
    """
    name = _("Card")
    default_css_class = 'card'
    require_parent = False
    parent_classes = ['BootstrapColumnPlugin']
    allow_children = True
    render_template = 'cascade/bootstrap4/card.html'
    glossary_field_order = ['header', 'body_padding', 'footer']

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapCardPlugin, cls).get_identifier(obj)
        try:
            return format_html('{0}{1}', identifier, obj.card_header or obj.card_footer)
        except AttributeError:
            pass
        return identifier

    @classmethod
    def get_child_classes(cls, slot, page, instance=None):
        """Restrict child classes of Card to one of each: Header, Body and Footer"""
        child_classes = super(BootstrapCardPlugin, cls).get_child_classes(slot, page, instance)
        # allow only one child of type Header, Body, Footer
        for child in instance.get_children():
            if child.plugin_type in child_classes:
                child_classes.remove(child.plugin_type)
        return child_classes

plugin_pool.register_plugin(BootstrapCardPlugin)
