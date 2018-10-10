# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2

from django import VERSION as DJANGO_VERSION
from django.forms import widgets
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentContainer
from .plugin_base import BootstrapPluginBase

card_heading_sizes = [('', _("normal"))] + [('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7)]


class CardTypeWidget(widgets.RadioSelect):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    CARD_TYPES = OrderedDict([
        ('card-primary', _("Primary")),
        ('card-success', _("Success")),
        ('card-info', _("Info")),
        ('card-warning', _("Warning")),
        ('card-danger', _("Danger"))
    ])
    template_name = 'cascade/forms/widgets/card_types.html'

    @classmethod
    def get_instance(cls):
        choices = tuple((k, v) for k, v in cls.CARD_TYPES.items())
        return cls(choices=choices)

    def render(self, name, value, attrs=None, renderer=None):
        if DJANGO_VERSION >= (1, 11):
            return super(CardTypeWidget, self).render(name, value, attrs, renderer)

        renderer = self.get_renderer(name, value, attrs)
        return format_html('<div class="form-row">{}</div>',
            format_html_join('\n', '<div class="field-box"><div class="card {1}">'
                '<div class="card-heading">{2}</div><div class="card-body">{3}</div>'
                '</div><div class="label">{0}</div></div>',
                ((force_text(w), w.choice_value, force_text(self.CARD_TYPES[w.choice_value]), _("Content"))
                 for w in renderer)
            ))


class BootstrapCardPlugin(TransparentContainer, BootstrapPluginBase):
    """
    Use this plugin to display a card with optional card-header and card-footer.
    """
    name = _("Card")
    default_css_class = 'card'
    require_parent = False
    parent_classes = ['BootstrapColumnPlugin']
    allow_children = True
    child_classes = None
    render_template = 'cascade/bootstrap4/card.html'
    glossary_field_order = ['card_type', 'heading_size', 'heading', 'footer']

    card_type = GlossaryField(
        CardTypeWidget.get_instance(),
        label=_("Card type"),
        help_text=_("Display Card using this style.")
    )

    heading_size = GlossaryField(
        widgets.Select(choices=card_heading_sizes),
        initial='',
        label=_("Heading Size")
    )

    heading = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Card Heading")
    )

    footer = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Card Footer")
    )

    html_parser = HTMLParser()

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapCardPlugin, cls).get_identifier(obj)
        heading = cls.html_parser.unescape(obj.glossary.get('heading', ''))
        return format_html('{0}{1}', identifier, heading)

    def render(self, context, instance, placeholder):
        heading = self.html_parser.unescape(instance.glossary.get('heading', ''))
        footer = self.html_parser.unescape(instance.glossary.get('footer', ''))
        context.update({
            'instance': instance,
            'card_type': instance.glossary.get('card_type', 'card-default'),
            'card_heading': heading,
            'heading_size': instance.glossary.get('heading_size', ''),
            'card_footer': footer,
            'placeholder': placeholder,
        })
        return self.super(BootstrapCardPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(BootstrapCardPlugin)
