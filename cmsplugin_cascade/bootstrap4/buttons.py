# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.conf import settings
from django.forms import widgets
from django.forms.fields import CharField
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from cmsplugin_cascade.link.forms import TextLinkFormMixin
if 'cmsplugin_cascade.icon' in settings.INSTALLED_APPS:
    from cmsplugin_cascade.icon.mixins import IconPluginMixin
else:
    from cmsplugin_cascade.plugin_base import CascadePluginMixinBase as IconPluginMixin


class ButtonTypeWidget(widgets.RadioSelect):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    BUTTON_TYPES = OrderedDict([
        ('btn-primary', _("Primary")),
        ('btn-secondary', _("Secondary")),
        ('btn-success', _("Success")),
        ('btn-danger', _("Danger")),
        ('btn-warning', _("Warning")),
        ('btn-info', _("Info")),
        ('btn-light', _("Light")),
        ('btn-dark', _("Dark")),
        ('btn-link', _("Link")),
        ('btn-outline-primary', _("Primary")),
        ('btn-outline-secondary', _("Secondary")),
        ('btn-outline-success', _("Success")),
        ('btn-outline-danger', _("Danger")),
        ('btn-outline-warning', _("Warning")),
        ('btn-outline-info', _("Info")),
        ('btn-outline-light', _("Light")),
        ('btn-outline-dark', _("Dark")),
        ('btn-outline-link', _("Link")),
    ])
    template_name = 'cascade/forms/widgets/button_types.html'

    @classmethod
    def get_instance(cls):
        return cls(choices=[(k, v) for k, v in cls.BUTTON_TYPES.items()])


class ButtonSizeWidget(widgets.RadioSelect):
    """
    Render sample buttons in different sizes in the button's backend editor.
    """
    BUTTON_SIZES = OrderedDict([
        ('btn-lg', _("Large button")),
        ('', _("Default button")),
        ('btn-sm', _("Small button")),
    ])
    template_name = 'cascade/forms/widgets/button_sizes.html'

    @classmethod
    def get_instance(cls):
        return cls(choices=[(k, v) for k, v in cls.BUTTON_SIZES.items()])


class BootstrapButtonMixin(IconPluginMixin):
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    render_template = 'cascade/bootstrap4/button.html'
    allow_children = False
    default_css_class = 'btn'
    default_css_attributes = ['button_type', 'button_size', 'button_options', 'quick_float', 'stretched_link']
    ring_plugin = 'ButtonMixin'
    require_icon_font = False

    button_type = GlossaryField(
        ButtonTypeWidget.get_instance(),
        label=_("Button Type"),
        initial='btn-primary',
        help_text=_("Display Link using this Button Style")
    )

    button_size = GlossaryField(
        ButtonSizeWidget.get_instance(),
        label=_("Button Size"),
        initial='',
        help_text=_("Display Link using this Button Size")
    )

    button_options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=[
            ('btn-block', _('Block level')),
            ('disabled', _('Disabled')),
        ]),
        label=_("Button Options"),
    )

    quick_float = GlossaryField(
        widgets.RadioSelect(choices=[
            ('', _("Do not float")),
            ('pull-left', _("Pull left")),
            ('pull-right', _("Pull right")),
        ]),
        label=_("Quick Float"),
        initial='',
        help_text=_("Float the button to the left or right.")
    )

    icon_align = GlossaryField(
        widgets.RadioSelect(choices=[
            ('', _("No Icon")),
            ('icon-left', _("Icon placed left")),
            ('icon-right', _("Icon placed right")),
        ]),
        label=_("Icon alignment"),
        initial='',
        help_text=_("Add an Icon before or after the button content.")
    )

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    stretched_link = GlossaryField(
        widgets.CheckboxInput(),
        label=_("Stretched link"),
        help_text=_("Stretched-link utility to make any anchor the size of it’s nearest position:\
         relative parent, perfect for entirely clickable cards!")
    )

    class Media:
        js = ['cascade/js/admin/buttonmixin.js']

    def render(self, context, instance, placeholder):
        context = super(BootstrapButtonMixin, self).render(context, instance, placeholder)
        try:
            icon_font = self.get_icon_font(instance)
            symbol = instance.glossary.get('symbol')
        except AttributeError:
            icon_font, symbol = None, None
        if icon_font and symbol:
            context['stylesheet_url'] = icon_font.get_stylesheet_url()
            mini_template = '{0}<i class="icon-{1} {2}" aria-hidden="true"></i>{3}'
            icon_align = instance.glossary.get('icon_align')
            if icon_align == 'icon-left':
                context['icon_left'] = format_html(mini_template, '', symbol, 'cascade-icon-left', ' ')
            elif icon_align == 'icon-right':
                context['icon_right'] = format_html(mini_template, ' ', symbol, 'cascade-icon-right', '')
        return context


class BootstrapButtonPlugin(BootstrapButtonMixin, LinkPluginBase):
    module = 'Bootstrap'
    name = _("Button")
    model_mixins = (LinkElementMixin,)
    fields = ['link_content'] + list(LinkPluginBase.fields)
    glossary_field_order = ['button_type', 'button_size', 'button_options', 'quick_float',
                            'target', 'title', 'icon_align', 'icon_font', 'symbol', 'stretched_link']
    ring_plugin = 'ButtonPlugin'
    DEFAULT_BUTTON_ATTRIBUTES = {'role': 'button'}

    class Media:
        css = {'all': ['cascade/css/admin/bootstrap4-buttons.css', 'cascade/css/admin/iconplugin.css']}
        js = ['cascade/js/admin/buttonplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapButtonPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('link_content')
        if not content:
            try:
                content = force_text(ButtonTypeWidget.BUTTON_TYPES[obj.glossary['button_type']])
            except KeyError:
                content = _("Empty")
        return format_html('{}{}', identifier, content)

    def get_form(self, request, obj=None, **kwargs):
        link_content = CharField(
            required=False,
            label=_("Button Content"),
            widget=widgets.TextInput(attrs={'size': 50}),
        )
        Form = type(str('ButtonForm'), (TextLinkFormMixin, getattr(LinkForm, 'get_form_class')(),),
                    {'link_content': link_content})
        kwargs.update(form=Form)
        return super(BootstrapButtonPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapButtonPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('stretched_link'):
            css_classes.append('stretched_link')
        return css_classes

    @classmethod
    def get_html_tag_attributes(cls, obj):
        attributes = cls.super(BootstrapButtonPlugin, cls).get_html_tag_attributes(obj)
        attributes.update(cls.DEFAULT_BUTTON_ATTRIBUTES)
        return attributes

plugin_pool.register_plugin(BootstrapButtonPlugin)
