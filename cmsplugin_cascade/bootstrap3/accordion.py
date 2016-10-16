# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.models import ModelForm
from django.forms.fields import IntegerField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.mixins import TransparentMixin
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase
from .panel import panel_heading_sizes, PanelTypeRenderer


class AccordionForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Panels"),
        help_text=_("Number of panels for this panel group."))


class BootstrapAccordionPlugin(TransparentMixin, BootstrapPluginBase):
    name = _("Accordion")
    form = AccordionForm
    default_css_class = 'panel-group'
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = True
    child_classes = None
    render_template = 'cascade/bootstrap3/{}/accordion.html'
    fields = ('num_children', 'glossary',)

    close_others = GlossaryField(
         widgets.CheckboxInput(),
         label=_("Close others"),
         initial=True,
         help_text=_("Open only one panel at a time.")
    )

    first_is_open = GlossaryField(
         widgets.CheckboxInput(),
         label=_("First panel open"),
         initial=True,
         help_text=_("Start with the first panel open.")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapAccordionPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} panel', 'with {0} panels', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(BootstrapAccordionPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, BootstrapAccordionPanelPlugin)

plugin_pool.register_plugin(BootstrapAccordionPlugin)


class BootstrapAccordionPanelPlugin(TransparentMixin, BootstrapPluginBase):
    name = _("Accordion Panel")
    default_css_class = 'panel-body'
    parent_classes = ('BootstrapAccordionPlugin',)
    require_parent = True
    alien_child_classes = True
    render_template = 'cascade/bootstrap3/{}/accordion-panel.html'

    panel_type = GlossaryField(
        PanelTypeRenderer.get_widget(),
        label=_("Panel type"),
        help_text=_("Display Panel using this style.")
    )

    heading_size = GlossaryField(
        widgets.Select(choices=panel_heading_sizes),
        initial='',
        label=_("Heading Size")
    )

    panel_title = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Panel Title")
    )

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapAccordionPanelPlugin, cls).get_identifier(obj)
        panel_title = HTMLParser().unescape(obj.glossary.get('panel_title', ''))
        panel_title = Truncator(panel_title).words(3, truncate=' ...')
        return format_html('{0}{1}', identifier, panel_title)

plugin_pool.register_plugin(BootstrapAccordionPanelPlugin)
