# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.forms import widgets
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentContainer
from .plugin_base import BootstrapPluginBase

panel_heading_sizes = (('', _("normal")),) + tuple(('h{}'.format(k), _("Heading {}").format(k)) for k in range(1, 7))


class PanelTypeWidget(widgets.RadioSelect):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    PANEL_TYPES = OrderedDict((('panel-default', _("Default")), ('panel-primary', _("Primary")),
        ('panel-success', _("Success")), ('panel-info', _("Info")), ('panel-warning', _("Warning")),
        ('panel-danger', _("Danger")),))

    @classmethod
    def get_instance(cls):
        choices = tuple((k, v) for k, v in cls.PANEL_TYPES.items())
        return cls(choices=choices)

    def render(self, name, value, attrs=None, renderer=None):
        renderer = self.get_renderer(name, value, attrs)
        return format_html('<div class="form-row">{}</div>',
            format_html_join('\n', '<div class="field-box"><div class="panel {1}">'
                '<div class="panel-heading">{2}</div><div class="panel-body">{3}</div>'
                '</div><div class="label">{0}</div></div>',
                ((force_text(w), w.choice_value, force_text(self.PANEL_TYPES[w.choice_value]), _("Content"))
                 for w in renderer)
            ))


class BootstrapPanelPlugin(TransparentContainer, BootstrapPluginBase):
    """
    Use this plugin to display a panel with optional panel-header and panel-footer.
    """
    name = _("Panel")
    default_css_class = 'panel'
    require_parent = False
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = True
    child_classes = None
    render_template = 'cascade/bootstrap3/panel.html'
    glossary_field_order = ('panel_type', 'heading_size', 'heading', 'footer')

    panel_type = GlossaryField(
        PanelTypeWidget.get_instance(),
        label=_("Panel type"),
        help_text=_("Display Panel using this style.")
    )

    heading_size = GlossaryField(
        widgets.Select(choices=panel_heading_sizes),
        initial='',
        label=_("Heading Size")
    )

    heading = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Panel Heading")
    )

    footer = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Panel Footer")
    )

    html_parser = HTMLParser()

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapPanelPlugin, cls).get_identifier(obj)
        heading = cls.html_parser.unescape(obj.glossary.get('heading', ''))
        return format_html('{0}{1}', identifier, heading)

    def render(self, context, instance, placeholder):
        heading = self.html_parser.unescape(instance.glossary.get('heading', ''))
        footer = self.html_parser.unescape(instance.glossary.get('footer', ''))
        context.update({
            'instance': instance,
            'panel_type': instance.glossary.get('panel_type', 'panel-default'),
            'panel_heading': heading,
            'heading_size': instance.glossary.get('heading_size', ''),
            'panel_footer': footer,
            'placeholder': placeholder,
        })
        return self.super(BootstrapPanelPlugin, self).render(context, instance, placeholder)

plugin_pool.register_plugin(BootstrapPanelPlugin)
