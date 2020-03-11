from django.forms import widgets, BooleanField, CharField
from django.forms.fields import IntegerField
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.utils.safestring import mark_safe 
from django.utils.text import Truncator
from django.utils.html import escape
from entangled.forms import EntangledModelFormMixin, EntangledFormField, EntangledForm
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.forms import ManageChildrenFormMixin, ManageNestedFormMixin
from cmsplugin_cascade.plugin_base import TransparentWrapper, TransparentContainer
from cmsplugin_cascade.widgets import NumberInputWidget
from .plugin_base import BootstrapPluginBase


class AccordionForm(EntangledForm):
    num_children = IntegerField(
        min_value=1,
        initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_("Groups"),
        help_text=_("Number of groups for this accordion."),
    )

    close_others = BooleanField(
         label=_("Close others"),
         initial=True,
         required=False,
         help_text=_("Open only one card at a time.")
    )

    first_is_open = BooleanField(
         label=_("First open"),
         initial=True,
         required=False,
         help_text=_("Start with the first card open.")
    )

class AccordionFormMixin(EntangledModelFormMixin, ManageNestedFormMixin):
    accordion_nested = EntangledFormField(AccordionForm)

    class Meta:
        untangled_fields = ['accordion_nested.num_children']
        entangled_fields = {'glossary': ['accordion_nested']}


class BootstrapAccordionPlugin(TransparentWrapper, BootstrapPluginBase):
    name = _("Accordion")
    default_css_class = 'accordion'
    require_parent = True
    parent_classes = ['BootstrapColumnPlugin']
    direct_child_classes = ['BootstrapAccordionGroupPlugin']
    allow_children = True
    form = AccordionFormMixin
    render_template = 'cascade/bootstrap4/{}accordion.html'

    @classmethod
    def get_identifier(cls, obj):
        num_cards = obj.get_num_children()
        content = ungettext_lazy('with {0} card', 'with {0} cards', num_cards).format(num_cards)
        return mark_safe(content)

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapAccordionPlugin, self).render(context, instance, placeholder)
        context.update({
            'close_others': instance.glossary.get('accordion_nested', {}).get('close_others', True),
            'first_is_open': instance.glossary.get('accordion_nested', {}).get('first_is_open', True),
        })
        return context

    def save_model(self, request, obj, form, change): 
        wanted_children = int(form.cleaned_data.get('accordion_nested.num_children'))
        super().save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, BootstrapAccordionGroupPlugin)

plugin_pool.register_plugin(BootstrapAccordionPlugin)


class AccordionGroupForm(EntangledForm):
    heading = CharField(
        label=_("Heading"),
        widget=widgets.TextInput(attrs={'size': 80}),
    )

    body_padding = BooleanField(
         label=_("Body with padding"),
         initial=True,
         required=False,
         help_text=_("Add standard padding to card body."),
    )

    def clean_heading(self):
        return escape(self.cleaned_data.get('heading'))


class AccordionGroupFormMixin( ManageNestedFormMixin, EntangledModelFormMixin):
    accordion_nested = EntangledFormField(AccordionGroupForm)

    class Meta:
        entangled_fields = {'glossary': ['accordion_nested']}


class BootstrapAccordionGroupPlugin(TransparentContainer, BootstrapPluginBase):
    name = _("Accordion Group")
    direct_parent_classes = parent_classes = ['BootstrapAccordionPlugin']
    render_template = 'cascade/generic/naked.html'
    require_parent = True
    form = AccordionGroupFormMixin
    alien_child_classes = True

    @classmethod
    def get_identifier(cls, instance):
        heading = instance.glossary.get('accordion_nested', {}).get('heading' , '')
        return Truncator(heading).words(3, truncate=' ...')

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapAccordionGroupPlugin, self).render(context, instance, placeholder)
        context.update({
            'heading': mark_safe(instance.glossary.get('accordion_nested', {}).get('heading' , '')),
            'no_body_padding': not instance.glossary.get('accordion_nested', {}).get('no_body_padding' , True),
        })
        return context

plugin_pool.register_plugin(BootstrapAccordionGroupPlugin)

