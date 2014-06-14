# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import MultipleInlineStylesWidget
from .plugin_base import BootstrapPluginBase


class ButtonTypeRenderer(RadioFieldRenderer):
    BUTTON_TYPES = SortedDict((('btn-default', _('Default')), ('btn-primary', _('Primary')),
        ('btn-success', _('Success')), ('btn-info', _('Info')), ('btn-warning', _('Warning')),
        ('btn-danger', _('Danger')), ('btn-link', _('Link')),))

    def render(self):
        return format_html('<div class="row">{0}</div>',
            format_html_join('\n', '<div class="col-sm-2 text-center"><button class="btn {1}">{2}</button><h4>{0}</h4></div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_TYPES[w.choice_value])) for w in self)
            ))


class ButtonSizeRenderer(RadioFieldRenderer):
    BUTTON_SIZES = SortedDict((('btn-lg', _('Large')), ('', _('Default')), ('btn-sm', _('Small')),
        ('btn-xs', _('Extra small')),))

    def render(self):
        return format_html('<div class="row">{0}</div>',
            format_html_join('\n', '<div class="col-sm-3 text-center">'
                '<p><button class="btn btn-primary {1}">{2}</button> <button class="btn btn-default {1}">{2}</button></p>'
                '<h4>{0}</h4></div>',
                ((force_text(w), w.choice_value, force_text(self.BUTTON_SIZES[w.choice_value])) for w in self)
            ))


class ButtonWrapperPlugin(BootstrapPluginBase):
    name = _("Button wrapper")
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cms/plugins/naked.html'
    generic_child_classes = ('LinkPlugin',)
    tag_type = None
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options',)
    partial_fields = (
        PartialFormField('button-type',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonTypeRenderer.BUTTON_TYPES.items()),
                                renderer=ButtonTypeRenderer),
                label=_('Button Type'),
                initial='btn-default'
        ),
        PartialFormField('button-size',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonSizeRenderer.BUTTON_SIZES.items()),
                                renderer=ButtonSizeRenderer),
                label=_('Button Size'),
                initial=''
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
                label=_('Button Options'),
        ),
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['margin-top', 'margin-right', 'margin-bottom', 'margin-left']),
            label=_('Inline Styles'),
            help_text=_('Margins for this button wrapper.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        return ButtonTypeRenderer.BUTTON_TYPES.get(obj.context.get('button-type'), '')

plugin_pool.register_plugin(ButtonWrapperPlugin)
