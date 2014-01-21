# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase


class ButtonWrapperPlugin(BootstrapPluginBase):
    name = _("Button wrapper")
    render_template = "cms/plugins/bootstrap/naked.html"
    child_classes = ['LinkPlugin']
    tag_type = 'naked'
    css_class_choices = (('btn', 'btn'),)
    #extra_classes_widget = MultipleRadioButtonsWidget((
    #    ('buttontype', (('', 'unstyled'),) + tuple(2 * ('btn-%s' % b,)
    #        for b in ('primary', 'info', 'success', 'warning', 'danger', 'inverse', 'link'))),
    #    ('buttonsize', (('', 'default'),) + tuple(2 * ('btn-%s' % b,)
    #        for b in ('large', 'small', 'mini',))),
    #))
    #tagged_classes_widget = MultipleCheckboxesWidget((('disabled', 'disabled'),))

plugin_pool.register_plugin(ButtonWrapperPlugin)
