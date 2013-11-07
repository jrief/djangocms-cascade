# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.models import modelform_factory
from django.utils.datastructures import SortedDict
from cms.plugin_base import CMSPluginBase
from cmsplugin_bootstrap.models import BootstrapElement

CSS_MARGIN_STYLES = ['margin-%s' % s for s in ('top', 'right', 'bottom', 'left')]
CSS_VERTICAL_SPACING = ['min-height']


class BootstrapPluginBase(CMSPluginBase):
    module = 'Bootstrap'
    model = BootstrapElement
    tag_type = 'div'
    change_form_template = "cms/plugins/bootstrap/change_form.html"
    render_template = "cms/plugins/bootstrap/generic.html"
    allow_children = True

    def __init__(self, *args, **kwargs):
        super(BootstrapPluginBase, self).__init__(*args, **kwargs)
        change_form_widgets = SortedDict()
        if hasattr(self, 'css_class_choices') and len(self.css_class_choices) > 1:
            change_form_widgets['class_name'] = widgets.Select(choices=self.css_class_choices)
        if hasattr(self, 'extra_classes_widget'):
            change_form_widgets['extra_classes'] = self.extra_classes_widget
        if hasattr(self, 'tagged_classes_widget'):
            change_form_widgets['tagged_classes'] = self.tagged_classes_widget
        if hasattr(self, 'extra_styles_widget'):
            change_form_widgets['extra_styles'] = self.extra_styles_widget
        if hasattr(self, 'options_widget'):
            change_form_widgets['options'] = self.options_widget
        self.form = modelform_factory(BootstrapElement, fields=change_form_widgets.keys(), widgets=change_form_widgets)

    def save_model(self, request, obj, form, change):
        obj.tag_type = self.tag_type
        if hasattr(self, 'css_class_choices') and len(self.css_class_choices) == 1:
            obj.class_name = self.css_class_choices[0][0]
        return super(BootstrapPluginBase, self).save_model(request, obj, form, change)
