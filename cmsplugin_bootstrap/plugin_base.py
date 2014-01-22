# -*- coding: utf-8 -*-
from django.forms.models import modelform_factory
from django.utils.text import Truncator
from cms.plugin_base import CMSPluginBase
from cmsplugin_bootstrap.models import BootstrapElement
from cmsplugin_bootstrap.widgets import JSONMultiWidget


class BootstrapPluginBase(CMSPluginBase):
    module = 'Bootstrap'
    model = BootstrapElement
    tag_type = 'div'
    change_form_template = "cms/admin/change_form.html"
    render_template = "cms/plugins/bootstrap/generic.html"
    allow_children = True

    def __init__(self, model=None, admin_site=None, data_widgets=None):
        super(BootstrapPluginBase, self).__init__(model, admin_site)
        if data_widgets:
            self.data_widgets = data_widgets
        elif not hasattr(self, 'data_widgets'):
            self.data_widgets = []

    def save_model(self, request, obj, form, change):
        # add defaults to data field, which are required for each element
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

    def get_form(self, request, obj=None, **kwargs):
        widgets = { 'extra_context': JSONMultiWidget(self.data_widgets) }
        form = modelform_factory(BootstrapElement, fields=['extra_context'], widgets=widgets)
        return form
