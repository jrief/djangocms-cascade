# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from collections import OrderedDict
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.forms import TextLinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.utils import resolve_dependencies
from .glyphicons import GlyphiconRenderer


class ButtonTypeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    BUTTON_TYPES = OrderedDict((('btn-default', _('Default')), ('btn-primary', _('Primary')),
        ('btn-success', _('Success')), ('btn-info', _('Info')), ('btn-warning', _('Warning')),
        ('btn-danger', _('Danger')), ('btn-link', _('Link')),))

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
    BUTTON_SIZES = OrderedDict((('btn-lg', _('Large')), ('', _('Default')), ('btn-sm', _('Small')),
        ('btn-xs', _('Extra small')),))

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


class BootstrapButtonMixin(object):
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin',)
    render_template = 'cascade/bootstrap3/button.html'
    allow_children = False
    text_enabled = True
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options', 'quick-float',)

    glossary_fields = (
        PartialFormField('button-type',
            ButtonTypeRenderer.get_widget(),
            label=_("Button Type"),
            initial='btn-default',
            help_text=_("Display Link using this Button Style")
        ),
        PartialFormField('button-size',
            ButtonSizeRenderer.get_widget(),
            label=_("Button Size"),
            initial='',
            help_text=_("Display Link using this Button Size")
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
            label=_("Button Options"),
        ),
        PartialFormField('quick-float',
            widgets.RadioSelect(choices=(('', _("Do not float")), ('pull-left', _("Pull left")), ('pull-right', _("Pull right")),)),
            label=_("Quick Float"),
            initial='',
            help_text=_("Float the button to the left or right.")
        ),
        PartialFormField('icon-left',
            GlyphiconRenderer.get_widget(),
            label=_("Prepend icon"),
            initial='',
            help_text=_("Prepend a Glyphicon before the content.")
        ),
        PartialFormField('icon-right',
            GlyphiconRenderer.get_widget(),
            label=_("Append icon"),
            initial='',
            help_text=_("Append a Glyphicon after the content.")
        ),
    )

    def render(self, context, instance, placeholder):
        context = super(BootstrapButtonMixin, self).render(context, instance, placeholder)
        mini_template = '{0}<span class="glyphicon glyphicon-{1}" aria-hidden="true"></span>{2}'
        nbsp = mark_safe('&nbsp;')
        icon_left = instance.glossary.get('icon-left')
        if icon_left:
            context['icon_left'] = format_html(mini_template, '', icon_left, nbsp)
        icon_right = instance.glossary.get('icon-right')
        if icon_right:
            context['icon_right'] = format_html(mini_template, nbsp, icon_right, '')
        return context


class BootstrapButtonPlugin(BootstrapButtonMixin, LinkPluginBase):
    module = 'Bootstrap'
    name = _("Button")
    form = TextLinkForm
    model_mixins = (LinkElementMixin,)
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)
    glossary_fields = BootstrapButtonMixin.glossary_fields + LinkPluginBase.glossary_fields

    class Media:
        css = {'all': ('cascade/css/admin/bootstrap.min.css', 'cascade/css/admin/bootstrap-theme.min.css',)}
        js = resolve_dependencies('cascade/js/admin/linkplugin.js')

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapButtonPlugin, cls).get_identifier(obj)
        content = obj.glossary.get('link_content')
        if not content:
            try:
                content = force_text(ButtonTypeRenderer.BUTTON_TYPES[obj.glossary['button-type']])
            except KeyError:
                content = _("Empty")
        return format_html('{}{}', identifier, content)

plugin_pool.register_plugin(BootstrapButtonPlugin)
