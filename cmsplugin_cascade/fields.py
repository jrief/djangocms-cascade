# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError


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
                except ValidationError as e:
                    if isinstance(getattr(e, 'params', None), dict):
                        e.params.update(label=self.label)
                    messages = self.error_class([m for m in e.messages])
                    errors.extend(messages)
        else:
            try:
                self.widget.validate(value.get(self.name))
            except ValidationError as e:
                if isinstance(getattr(e, 'params', None), dict):
                    e.params.update(label=self.label)
                errors = self.error_class([m for m in e.messages])
        if errors:
            raise ValidationError(errors)
