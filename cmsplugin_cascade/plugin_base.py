# -*- coding: utf-8 -*-
from django.forms.models import modelform_factory
from django.forms import widgets
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.widgets import JSONMultiWidget


class CascadePluginBase(CMSPluginBase):
    model = CascadeElement
    tag_type = 'div'
    change_form_template = 'cms/admin/change_form.html'
    render_template = 'cms/plugins/generic.html'

    def _child_classes(self):
        """All registered plugins shall be allowed as children for this plugin"""
        result = list(getattr(self, 'generic_child_classes', [])) or []
        if result:
            for p in plugin_pool.get_all_plugins():
                if isinstance(p.parent_classes, (list, tuple)) and self.__class__.__name__ in p.parent_classes \
                    and p.__name__ not in result:
                    result.append(p.__name__)
            return result
        else:
            return None  # All classes will be available
    child_classes = property(_child_classes)

    def __init__(self, model=None, admin_site=None, partial_fields=None):
        super(CascadePluginBase, self).__init__(model, admin_site)
        if partial_fields:
            self.partial_fields = partial_fields
        elif not hasattr(self, 'partial_fields'):
            self.partial_fields = []

    @classmethod
    def get_identifier(cls, model):
        """
        Returns the descriptive name for the current model
        """
        return u''

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        for attr in getattr(cls, 'default_css_attributes', []):
            css_class = obj.context.get(attr)
            if isinstance(css_class, basestring):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = obj.context.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_data_options(cls, obj):
        data_options = getattr(cls, 'default_data_options', {})
        instance_options = obj.context.get('data_options')
        if instance_options:
            data_options.update(instance_options)
        return data_options

    def get_object(self, request, object_id):
        """
        Get the object and augment its context with the number of children.
        """
        obj = super(CascadePluginBase, self).get_object(request, object_id)
        if obj and isinstance(obj.context, dict):
            obj.context['-num-children-'] = obj.get_children().count()
        return obj

    def save_model(self, request, obj, form, change):
        """
        Save the object in the database and remove temporary context item '-num-children-'.
        """
        if isinstance(obj.context, dict) and '-num-children-' in obj.context:
            del obj.context['-num-children-']
        super(CascadePluginBase, self).save_model(request, obj, form, change)

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
        form = modelform_factory(CascadeElement, fields=['context'], widgets=widgets)
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
