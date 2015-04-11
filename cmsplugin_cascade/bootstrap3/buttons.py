# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.link.forms import TextLinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.utils import resolve_dependencies


class ButtonTypeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different colors in the button's backend editor.
    """
    BUTTON_TYPES = SortedDict((('btn-default', _('Default')), ('btn-primary', _('Primary')),
        ('btn-success', _('Success')), ('btn-info', _('Info')), ('btn-warning', _('Warning')),
        ('btn-danger', _('Danger')), ('btn-link', _('Link')),))

    def render(self):
        return format_html('<div class="form-row">{0}</div>',
            format_html_join('\n', '<div class="field-box">'
                             '<span class="btn {1}">{2}</span>'
                             '<div class="label">{0}</div></div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_TYPES[w.choice_value])) for w in self)
            ))


class ButtonSizeRenderer(RadioFieldRenderer):
    """
    Render sample buttons in different sizes in the button's backend editor.
    """
    BUTTON_SIZES = SortedDict((('btn-lg', _('Large')), ('', _('Default')), ('btn-sm', _('Small')),
        ('btn-xs', _('Extra small')),))

    def render(self):
        return format_html('<div class="form-row">{0}</div>',
            format_html_join('\n',
                '<div class="field-box"><div class="button-samples">'
                    '<span class="btn btn-primary {1}">{2}</span>'
                    '<span class="btn btn-default {1}">{2}</span></div>'
                    '<div class="label">{0}</div>'
                '</div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_SIZES[w.choice_value])) for w in self)
            ))


class BootstrapButtonPlugin(LinkPluginBase):
    module = 'Bootstrap'
    name = _("Button")
    form = TextLinkForm
    model_mixins = (LinkElementMixin,)
    parent_classes = ('BootstrapColumnPlugin',)
    render_template = 'cascade/bootstrap3/button.html'
    allow_children = False
    text_enabled = True
    tag_type = None
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options', 'quick-float',)
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)
    glossary_fields = (
        PartialFormField('button-type',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonTypeRenderer.BUTTON_TYPES.items()),
                                renderer=ButtonTypeRenderer),
            label=_('Button Type'),
            initial='btn-default',
            help_text=_("Display Link using this Button Style")
        ),
        PartialFormField('button-size',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonSizeRenderer.BUTTON_SIZES.items()),
                                renderer=ButtonSizeRenderer),
            label=_('Button Size'),
            initial='',
            help_text=_("Display Link using this Button Size")
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
            label=_('Button Options'),
        ),
        PartialFormField('quick-float',
            widgets.RadioSelect(choices=(('', _("Do not float")), ('pull-left', _("Pull left")), ('pull-right', _("Pull right")),)),
            label=_('Quick Float'),
            initial='',
            help_text=_("Float the button to the left or right.")
        ),
    ) + LinkPluginBase.glossary_fields

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
