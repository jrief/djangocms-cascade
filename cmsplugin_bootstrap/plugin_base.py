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

    def __init__(self, model=None, admin_site=None, context_widgets=None):
        super(BootstrapPluginBase, self).__init__(model, admin_site)
        if context_widgets:
            self.context_widgets = context_widgets
        elif not hasattr(self, 'context_widgets'):
            self.context_widgets = []

    def save_model(self, request, obj, form, change):
        obj.set_defaults(self)
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
        widgets = { 'context': JSONMultiWidget(self.context_widgets) }
        form = modelform_factory(BootstrapElement, fields=['context'], widgets=widgets)
        return form
