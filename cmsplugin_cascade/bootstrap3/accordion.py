# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator
from django.utils.html import format_html
from django.forms.models import ModelForm
from django.forms.fields import IntegerField
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase
from cmsplugin_cascade.mixins import TransparentMixin


class AccordionForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em;'}),
        label=_("Panels"),
        help_text=_("Number of panels for this panel group."))


class AccordionPlugin(TransparentMixin, BootstrapPluginBase):
    name = _("Accordion")
    form = AccordionForm
    default_css_class = 'panel-group'
    require_parent = False
    parent_classes = None
    allow_children = True
    child_classes = None
    render_template = 'cascade/bootstrap3/accordion.html'
    fields = ('num_children', 'glossary',)
    glossary_fields = (
        PartialFormField('close_others',
            widgets.CheckboxInput(),
            label=_("Close others"),
            initial=True,
            help_text=_("Open only one panel at a time.")
        ),
        PartialFormField('first_is_open',
            widgets.CheckboxInput(),
            label=_("First panel open"),
            initial=True,
            help_text=_("Start with the first panel open.")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(AccordionPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} panel', 'with {0} panels', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(AccordionPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, AccordionPanelPlugin)

plugin_pool.register_plugin(AccordionPlugin)


class AccordionPanelPlugin(TransparentMixin, BootstrapPluginBase):
    name = _("Accordion Panel")
    default_css_class = 'panel-body'
    parent_classes = ('AccordionPlugin',)
    require_parent = True
    alien_child_classes = True
    glossary_fields = (
        PartialFormField('panel_title',
            widgets.TextInput(attrs={'size': 150}),
            label=_("Panel Title")
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(AccordionPanelPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('panel_title', '')
        if content:
            content = unicode(Truncator(content).words(3, truncate=' ...'))
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(AccordionPanelPlugin)
