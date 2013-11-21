# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.change_form_widgets import ExtraStylesWidget, MultipleRadioButtonsWidget
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, CSS_VERTICAL_SPACING


class BootstrapRowPlugin(BootstrapPluginBase):
    name = _("Row container")
    child_classes = ['BootstrapColumnPlugin']
    tag_type = 'div'
    css_class_choices = (('row', 'row'), ('row-fluid', 'row-fluid'))
    extra_styles_widget = ExtraStylesWidget(CSS_VERTICAL_SPACING)

plugin_pool.register_plugin(BootstrapRowPlugin)


class BootstrapColumnPlugin(BootstrapPluginBase):
    name = _("Column container")
    parent_classes = ['BootstrapRowPlugin']
    require_parent = True
    tag_type = 'div'
    css_class_choices = tuple(2 * ('span%s' % i,) for i in range(1, 13))
    extra_classes_widget = MultipleRadioButtonsWidget((
        ('offset', (('', 'no offset'),) + tuple(2 * ('offset%s' % o,) for o in range(1, 12))),
    ))
    extra_styles_widget = ExtraStylesWidget(CSS_VERTICAL_SPACING)

plugin_pool.register_plugin(BootstrapColumnPlugin)


class BootstrapDivPlugin(BootstrapPluginBase):
    name = _("Simple div container")
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    tag_type = 'div'
    css_class_choices = (('', '---'), ('hero-unit', 'hero-unit'))
    extra_styles_widget = ExtraStylesWidget(CSS_VERTICAL_SPACING)

plugin_pool.register_plugin(BootstrapDivPlugin)


class HorizontalRulePlugin(BootstrapPluginBase):
    name = _("Horizontal Rule")
    require_parent = False
    allow_children = False
    tag_type = 'hr'
    render_template = 'cms/plugins/bootstrap/single.html'
    extra_styles_widget = ExtraStylesWidget(['margin-top', 'margin-bottom'])

plugin_pool.register_plugin(HorizontalRulePlugin)
