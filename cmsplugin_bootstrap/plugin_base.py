# -*- coding: utf-8 -*-
from django.forms.models import modelform_factory
from django.utils.text import Truncator
from cms.plugin_base import CMSPluginBase
from cmsplugin_bootstrap.models import BootstrapElement
from cmsplugin_bootstrap.widgets import JSONMultiWidget

CSS_VERTICAL_SPACING = ['min-height']


class BootstrapPluginBase(CMSPluginBase):
    module = 'Bootstrap'
    model = BootstrapElement
    tag_type = 'div'
    change_form_template = "cms/admin/change_form.html"
    render_template = "cms/plugins/bootstrap/generic.html"
    allow_children = True

    def __init__(self, *args, **kwargs):
        super(BootstrapPluginBase, self).__init__(*args, **kwargs)
        data_widgets = getattr(self, 'context_widgets', [])[:]
        widgets = { 'extra_context': JSONMultiWidget(data_widgets) }
        self.form = modelform_factory(BootstrapElement, fields=['extra_context'], widgets=widgets)

    def save_model(self, request, obj, form, change):
        if not isinstance(obj.extra_context, dict):
            obj.extra_context = {}
        obj.extra_context.setdefault('tag_type', self.tag_type)
        if hasattr(self, 'default_css_class'):
            obj.extra_context.setdefault('default_css_class', self.default_css_class)
        return super(BootstrapPluginBase, self).save_model(request, obj, form, change)

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        value = model.css_classes
        if value:
            return unicode(Truncator(value).words(3, truncate=' ...'))
        return u''

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super(BootstrapPluginBase, self).render_change_form(request, context, add, change, form_url, obj)
        return response
