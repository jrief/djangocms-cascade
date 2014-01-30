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
    change_form_template = 'cms/admin/change_form.html'
    render_template = 'cms/plugins/bootstrap/generic.html'
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
    def get_css_classes(cls, obj):
        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        for attr in getattr(cls, 'default_css_attributes', []):
            css_class = obj.context.get(attr)
            if css_class:
                css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = obj.context.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    def get_object(self, request, object_id):
        """
        Get the object and augment its context with the number of children.
        """
        obj = super(BootstrapPluginBase, self).get_object(request, object_id)
        if obj:
            obj.context['-num-children-'] = obj.get_children().count()
        return obj

    def save_model(self, request, obj, form, change):
        """
        Save the object in the database and remove temporary context item '-num-children-'.
        """
        if '-num-children-' in obj.context:
            del obj.context['-num-children-']
        super(BootstrapPluginBase, self).save_model(request, obj, form, change)

    def extend_children(self, parent, wanted_children, child_class, child_context=None):
        """
        Extend the number of children so that the parent object contains wanted children. No child
        will be removed.
        """
        from cms.api import add_plugin
        current_children = parent.get_children().count()
        for _ in range(current_children, wanted_children):
            child = add_plugin(parent.placeholder, child_class, parent.language, target=parent)
            if isinstance(child_context, dict):
                child.context.update(child_context)
            child.save()

    def get_form(self, request, obj=None, **kwargs):
        """
        Build the form used for changing the model.
        """
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
        self.initial = initial or ''
        self.help_text = help_text or ''
        self.error_class = error_class

    def run_validators(self, value):
        if not callable(getattr(self.widget, 'validate', None)):
            return
        errors = []
        if callable(getattr(self.widget, '__iter__', None)):
            for field_name in self.widget:
                try:
                    self.widget.validate(value.get(self.name), field_name)
                except ValidationError, e:
                    params = { 'label': self.label }
                    if e.params:
                        params.update(e.params)
                    messages = self.error_class([m % params for m in e.messages])
                    errors.extend(messages)
        else:
            try:
                self.widget.validate(value.get(self.name))
            except ValidationError, e:
                params = { 'label': self.label }
                if e.params:
                    params.update(e.params)
                errors = self.error_class([m % params for m in e.messages])
        if errors:
            raise ValidationError(errors)
