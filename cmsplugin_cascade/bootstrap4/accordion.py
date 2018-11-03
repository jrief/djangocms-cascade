# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.forms import widgets
from django.forms.models import ModelForm
from django.forms.fields import IntegerField
from django.utils.functional import cached_property
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.text import Truncator, mark_safe
from django.utils.html import format_html
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import TransparentWrapper, TransparentContainer
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase

html_parser = HTMLParser()


class AccordionForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Groups"),
        help_text=_("Number of groups for this accordion."))


class BootstrapAccordionPlugin(TransparentWrapper, BootstrapPluginBase):
    name = _("Accordion")
    form = AccordionForm
    default_css_class = 'accordion'
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    direct_child_classes = ['BootstrapAccordionGroupPlugin']
    allow_children = True
    render_template = 'cascade/bootstrap4/{}/accordion.html'
    fields = ['num_children', 'glossary']

    close_others = GlossaryField(
         widgets.CheckboxInput(),
         label=_("Close others"),
         initial=True,
         help_text=_("Open only one card at a time.")
    )

    first_is_open = GlossaryField(
         widgets.CheckboxInput(),
         label=_("First open"),
         initial=True,
         help_text=_("Start with the first card open.")
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapAccordionPlugin, cls).get_identifier(obj)
        num_cards = obj.get_num_children()
        content = ungettext_lazy('with {0} card', 'with {0} cards', num_cards).format(num_cards)
        return format_html('{0}{1}', identifier, content)

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(BootstrapAccordionPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, BootstrapAccordionGroupPlugin)

plugin_pool.register_plugin(BootstrapAccordionPlugin)


class BootstrapAccordionGroupMixin(object):
    @cached_property
    def heading(self):
        return mark_safe(html_parser.unescape(self.glossary.get('heading', '')))

    @cached_property
    def no_body_padding(self):
        return not self.glossary.get('body_padding', True)


class BootstrapAccordionGroupPlugin(TransparentContainer, BootstrapPluginBase):
    name = _("Accordion Group")
    direct_parent_classes = parent_classes = ['BootstrapAccordionPlugin']
    render_template = 'cascade/generic/naked.html'
    model_mixins = (BootstrapAccordionGroupMixin,)
    require_parent = True
    alien_child_classes = True
    glossary_field_order = ['heading', 'body_padding']

    heading = GlossaryField(
        widgets.TextInput(attrs={'size': 80}),
        label=_("Heading")
    )

    body_padding = GlossaryField(
         widgets.CheckboxInput(),
         label=_("Body with padding"),
         initial=True,
         help_text=_("Add standard padding to card body."),
    )

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapAccordionGroupPlugin, cls).get_identifier(obj)
        heading = HTMLParser().unescape(obj.glossary.get('heading', ''))
        heading = Truncator(heading).words(3, truncate=' ...')
        return format_html('{0}{1}', identifier, heading)

plugin_pool.register_plugin(BootstrapAccordionGroupPlugin)
