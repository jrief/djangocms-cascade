from typing import Optional

from django.forms import widgets, BooleanField, CharField
from django.forms.fields import IntegerField
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import gettext, gettext_lazy as _, ngettext

from cms.models import Page, CMSPlugin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.mixins import VerticalMarginsMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase, logger
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.mixins import ManageChildrenMixin
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.widgets import NumberInputWidget

from formset.forms import ModelForm


class AccordionForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(
        min_value=1,
        initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Items"),
        help_text=_("Number of items for this accordion."),
    )
    first_is_open = BooleanField(
         label=_("First open"),
         initial=True,
         required=False,
         help_text=_("Start with the first item open.")
    )
    close_others = BooleanField(
         label=_("Close others"),
         initial=True,
         required=False,
         help_text=_("Open only one item at a time.")
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['first_is_open', 'close_others']}



class BootstrapAccordionPlugin(VerticalMarginsMixin, ManageChildrenMixin, BootstrapPluginBase):
    name = _("Accordion")
    default_css_class = 'accordion'
    require_parent = True
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    form = AccordionForm
    render_template = 'cascade/bootstrap5/accordion.html'

    @classmethod
    def get_identifier(cls, obj):
        num_cards = obj.get_num_children()
        content = ngettext('with {0} item', 'with {0} items', num_cards).format(num_cards)
        return mark_safe(content)

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapAccordionPlugin, self).render(context, instance, placeholder)
        context.update({
            'close_others': instance.glossary.get('close_others', True),
            'first_is_open': instance.glossary.get('first_is_open', True),
        })
        return context

    def save_model(self, request, instance, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, instance, form, change)
        child_glossary = {'heading': gettext("Extra Accordion")}
        self.extend_children(instance, wanted_children, BootstrapAccordionItemPlugin, child_glossary=child_glossary)

plugin_pool.register_plugin(BootstrapAccordionPlugin)


class AccordionItemForm(ModelForm):
    heading = CharField(
        label=_("Heading"),
        widget=widgets.TextInput(attrs={'size': 80}),
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['heading']}

    def clean_heading(self):
        return escape(self.cleaned_data['heading'])


class BootstrapAccordionItemPlugin(BootstrapPluginBase):
    name = _("Accordion Item")
    parent_classes = ['BootstrapAccordionPlugin']
    cache_child_classes = False
    render_template = 'cascade/bootstrap5/accordion-item.html'
    require_parent = True
    form = AccordionItemForm

    @classmethod
    def get_identifier(cls, instance):
        heading = instance.glossary.get('heading', '')
        return Truncator(heading).words(3, truncate=' ...')

    @classmethod
    def get_child_classes(cls, slot, page: Optional[Page] = None, instance: Optional[CMSPlugin] = None, only_uncached: bool = False):
        child_classes = super().get_child_classes(slot, page, instance, only_uncached)
        if isinstance(instance.parent, BootstrapAccordionPlugin.model):
            if instance.parent.parent:
                _, plugin_class = instance.parent.parent.get_plugin_instance()
                child_classes.extend(plugin_class.get_child_classes(slot, page, instance.parent, only_uncached))
        else:
            logger.error(f"Could not find parent of type {BootstrapAccordionPlugin.model} for instance {instance}")
        return child_classes

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapAccordionItemPlugin, self).render(context, instance, placeholder)
        context.update({
            'heading': mark_safe(instance.glossary.get('heading', '')),
            'no_body_padding': not instance.glossary.get('body_padding', True),
        })
        return context


plugin_pool.register_plugin(BootstrapAccordionItemPlugin)
