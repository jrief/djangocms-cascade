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
from cmsplugin_cascade.link.models import LinkElement
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase


class ButtonTypeRenderer(RadioFieldRenderer):
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
    model = LinkElement
    form = LinkForm
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cms/bootstrap3/button.html'
    allow_children = False
    text_enabled = True
    tag_type = None
    default_css_class = 'btn'
    default_css_attributes = ('button-type', 'button-size', 'button-options',)
    fields = ('link_content', ('link_type', 'page_link', 'url', 'email'), 'glossary',)
    glossary_fields = (
        PartialFormField('button-type',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonTypeRenderer.BUTTON_TYPES.items()),
                                renderer=ButtonTypeRenderer),
                label=_('Button Type'), initial='btn-default',
                help_text=_("Display Link using this Button Style")
        ),
        PartialFormField('button-size',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonSizeRenderer.BUTTON_SIZES.items()),
                                renderer=ButtonSizeRenderer),
                label=_('Button Size'), initial='',
                help_text=_("Display Link using this Button Size")
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

    class Media:
        css = {'all': ('admin/css/bootstrap.min.css', 'admin/css/bootstrap-theme.min.css',)}

    @classmethod
    def get_identifier(cls, obj):
        button_type = ButtonTypeRenderer.BUTTON_TYPES.get(obj.glossary.get('button-type'))
        if button_type:
            button_type = ' ({0})'.format(force_text(button_type))
        link_content = obj.glossary.get('link_content', '')
        return link_content + button_type

plugin_pool.register_plugin(BootstrapButtonPlugin)
