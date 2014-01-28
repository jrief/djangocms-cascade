# -*- coding: utf-8 -*-
from django.forms.models import modelform_factory
from django.forms import widgets
from django.forms.util import ErrorList
from django.utils.text import Truncator
from django.core.exceptions import ValidationError
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

    def __init__(self, model=None, admin_site=None, partial_fields=None):
        super(BootstrapPluginBase, self).__init__(model, admin_site)
        if partial_fields:
            self.partial_fields = partial_fields
        elif not hasattr(self, 'partial_fields'):
            self.partial_fields = []

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        value = model.css_classes
        if value:
            return unicode(Truncator(value).words(3, truncate=' ...'))
        return u''

    @classmethod
    def get_css_classes(cls, model):
        if hasattr(cls, 'default_css_class'):
            return [cls.default_css_class]
        return []

    @classmethod
    def get_inline_styles(cls, model):
        return {}

    def get_form(self, request, obj=None, **kwargs):
        widgets = { 'context': JSONMultiWidget(self.partial_fields) }
        form = modelform_factory(BootstrapElement, fields=['context'], widgets=widgets)
        for field in self.partial_fields:
            form.base_fields['context'].validators.append(field.run_validators)
        setattr(form, 'partial_fields', self.partial_fields)
        return form


class PartialFormField(object):
    """
    Behave similar to django.forms.Field, encapsulating a partial dictionary, stored as
    JSONField in the database.
    """
    def __init__(self, name, widget, label=None, initial=None, error_class=ErrorList, help_text=''):
        if not name:
            raise AttributeError('The field must have a name')
        self.name = name
        if not label:
            self.label = name
        else:
            self.label = label
        if not isinstance(widget, widgets.Widget):
            raise AttributeError('The field `widget` must be derived from django.forms.name')
        self.widget = widget
        self.initial = initial or None
        self.help_text = help_text or None
        self.error_class = error_class

    def run_validators(self, value):
        if not callable(getattr(self.widget, 'validate', None)):
            return
        errors = []
        for field_name in self.widget:
            try:
                self.widget.validate(value.get(self.name), field_name)
            except ValidationError, e:
                params = { 'label': self.label }
                if e.params:
                    params.update(e.params)
                messages = self.error_class([m % params for m in e.messages])
                errors.extend(messages)
        if errors:
            raise ValidationError(errors)
