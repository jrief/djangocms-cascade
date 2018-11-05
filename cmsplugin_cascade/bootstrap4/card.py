# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2

from django.forms import widgets
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.text import mark_safe
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentContainer
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase

html_parser = HTMLParser()


class BootstrapCardMixin(object):
    @cached_property
    def card_header(self):
        return mark_safe(html_parser.unescape(self.glossary.get('header', '')))

    @cached_property
    def no_body_padding(self):
        return not self.glossary.get('body_padding', True)

    @cached_property
    def card_footer(self):
        return mark_safe(html_parser.unescape(self.glossary.get('footer', '')))


class BootstrapCardPlugin(TransparentContainer, BootstrapPluginBase):
    """
    Use this plugin to display a card with optional card-header and card-footer.
    """
    name = _("Card")
    default_css_class = 'card'
    require_parent = False
    parent_classes = ['BootstrapColumnPlugin']
    model_mixins = (BootstrapCardMixin,)
    allow_children = True
    child_classes = None
    render_template = 'cascade/bootstrap4/card.html'
    glossary_field_order = ['header', 'body_padding', 'footer']

    header = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Card Header")
    )

    body_padding = GlossaryField(
         widgets.CheckboxInput(),
         label=_("Body with padding"),
         initial=True,
         help_text=_("Add standard padding to card body.")
    )

    footer = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Card Footer")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapCardPlugin, cls).get_identifier(obj)
        return format_html('{0}{1}', identifier, obj.card_header or obj.card_footer)

plugin_pool.register_plugin(BootstrapCardPlugin)
