# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from django.forms import widgets
from django.forms.fields import CharField
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from cmsplugin_cascade.link.forms import TextLinkFormMixin
from .glyphicons import GlyphiconRenderer


class ButtonTypeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    BUTTON_TYPES = OrderedDict((('btn-default', _("Default")), ('btn-primary', _("Primary")),
        ('btn-success', _("Success")), ('btn-info', _("Info")), ('btn-warning', _("Warning")),
        ('btn-danger', _("Danger")), ('btn-link', _("Link")),))

    @classmethod
    def get_widget(cls):
        choices = tuple((k, v) for k, v in cls.BUTTON_TYPES.items())
        return widgets.RadioSelect(choices=choices, renderer=cls)

    def render(self):
        return format_html('<div class="form-row">{}</div>',
            format_html_join('\n', '<div class="field-box">'
                             '<span class="btn {1}">{2}</span>'
                             '<div class="label">{0}</div></div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_TYPES[w.choice_value])) for w in self)
            ))


class ButtonSizeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different sizes in the button's backend editor.
    """
    BUTTON_SIZES = OrderedDict((('btn-lg', _("Large")), ('', _("Default")), ('btn-sm', _("Small")),
        ('btn-xs', _("Extra small")),))

    @classmethod
    def get_widget(cls):
        choices = tuple((k, v) for k, v in cls.BUTTON_SIZES.items())
        return widgets.RadioSelect(choices=choices, renderer=cls)

    def render(self):
        return format_html('<div class="form-row">{}</div>',
            format_html_join('\n',
                '<div class="field-box"><div class="button-samples">'
                    '<span class="btn btn-primary {1}">{2}</span>'
                    '<span class="btn btn-default {1}">{2}</span></div>'
                    '<div class="label">{0}</div>'
                '</div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_SIZES[w.choice_value])) for w in self)
            ))


class BootstrapButtonMixin(CascadePluginMixinBase):
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    render_template = 'cascade/bootstrap3/button.html'
    allow_children = False
    text_enabled = True
    default_css_class = 'btn'
    default_css_attributes = ('button_type', 'button_size', 'button_options', 'quick_float',)

    button_type = GlossaryField(
        ButtonTypeRenderer.get_widget(),
        label=_("Button Type"),
        initial='btn-default',
        help_text=_("Display Link using this Button Style")
    )

    button_size = GlossaryField(
        ButtonSizeRenderer.get_widget(),
        label=_("Button Size"),
        initial='',
        help_text=_("Display Link using this Button Size")
    )

    button_options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
        label=_("Button Options"),
    )

    quick_float = GlossaryField(
        widgets.RadioSelect(choices=(('', _("Do not float")), ('pull-left', _("Pull left")),
                                     ('pull-right', _("Pull right")),)),
        label=_("Quick Float"),
        initial='',
        help_text=_("Float the button to the left or right.")
    )

    icon_left = GlossaryField(
        GlyphiconRenderer.get_widget(),
        label=_("Prepend icon"),
        initial='',
        help_text=_("Prepend a Glyphicon before the content.")
    )

    icon_right = GlossaryField(
        GlyphiconRenderer.get_widget(),
        label=_("Append icon"),
        initial='',
        help_text=_("Append a Glyphicon after the content.")
    )

    def render(self, context, instance, placeholder):
        context = super(BootstrapButtonMixin, self).render(context, instance, placeholder)
        mini_template = '{0}<span class="glyphicon glyphicon-{1} {2}" aria-hidden="true"></span>{3}'
        icon_left = instance.glossary.get('icon_left')
        if icon_left:
            context['icon_left'] = format_html(mini_template, '', icon_left, 'cascade-icon-left', ' ')
        icon_right = instance.glossary.get('icon_right')
        if icon_right:
            context['icon_right'] = format_html(mini_template, ' ', icon_right, 'cascade-icon-right', '')
        return context


class BootstrapButtonPlugin(BootstrapButtonMixin, LinkPluginBase):
    module = 'Bootstrap'
    name = _("Button")
    model_mixins = (LinkElementMixin,)
    fields = ('link_content',) + LinkPluginBase.fields
    glossary_field_order = ('button_type', 'button_size', 'button_options', 'quick_float',
                       'icon_left', 'icon_right')

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapButtonPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('link_content')
        if not content:
            try:
                content = force_text(ButtonTypeRenderer.BUTTON_TYPES[obj.glossary['button_type']])
            except KeyError:
                content = _("Empty")
        return format_html('{}{}', identifier, content)

    def get_form(self, request, obj=None, **kwargs):
        link_content = CharField(required=False, label=_("Button Content"), widget=widgets.TextInput())
        Form = type(str('ButtonForm'), (TextLinkFormMixin, getattr(LinkForm, 'get_form_class')(),),
                    {'link_content': link_content})
        kwargs.update(form=Form)
        return super(BootstrapButtonPlugin, self).get_form(request, obj, **kwargs)

plugin_pool.register_plugin(BootstrapButtonPlugin)
