# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.widgets import RadioFieldRenderer
from django.utils.html import format_html, format_html_join
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import CascadePluginBase, PartialFormField


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


class ButtonWrapperPlugin(CascadePluginBase):
    name = _("Button wrapper")
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cms/plugins/naked.html'
    generic_child_classes = ['LinkPlugin']
    tag_type = None
    partial_fields = (
        PartialFormField('button-type',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonTypeRenderer.BUTTON_TYPES.items()),
                                renderer=ButtonTypeRenderer),
                label=_('Button Type'), initial='default'
        ),
        PartialFormField('button-size',
            widgets.RadioSelect(choices=((k, v) for k, v in ButtonSizeRenderer.BUTTON_SIZES.items()),
                                renderer=ButtonSizeRenderer),
                label=_('Button Size'), initial=''
        ),
        PartialFormField('button-options',
            widgets.CheckboxSelectMultiple(choices=(('btn-block', _('Block level')), ('disabled', _('Disabled')),)),
                label=_('Button Options'),
        ),
    )

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = ['btn']
        for attr in ('button-type', 'button-size', 'button-options',):
            css_class = obj.context.get(attr)
            if isinstance(css_class, basestring):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        return ButtonTypeRenderer.BUTTON_TYPES.get(obj.context.get('button-type'), '')

plugin_pool.register_plugin(ButtonWrapperPlugin)
