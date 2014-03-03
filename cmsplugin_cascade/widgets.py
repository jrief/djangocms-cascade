# -*- coding: utf-8 -*-
import re
import json
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.html import escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _

CSS_MARGIN_STYLES = ['margin-%s' % s for s in ('top', 'right', 'bottom', 'left')]
CSS_VERTICAL_SPACING = ['min-height']


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def __init__(self, partial_fields):
        unique_keys = set([field.name for field in partial_fields])
        if len(partial_fields) > len(unique_keys):
            raise AttributeError('List of partial_fields may contain only unique keys')
        self.partial_fields = partial_fields[:]
        super(JSONMultiWidget, self).__init__((field.widget for field in partial_fields))

    def decompress(self, values):
        if not isinstance(values, dict):
            values = json.loads(values or '{}')
        for field in self.partial_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                values[field.name] = field.widget.decompress(values.get(field.name))
            else:
                values.setdefault(field.name, field.initial)
        return values

    def value_from_datadict(self, data, files, name):
        result = {}
        for field in self.partial_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                result[field.name] = field.widget.value_from_datadict(data, files, field.name)
            elif getattr(field.widget, 'allow_multiple_selected', False):
                result[field.name] = map(escape, data.getlist(field.name))
            else:
                result[field.name] = escape(data.get(field.name))
        return result

    def render(self, name, values, attrs):
        values = self.decompress(values)
        html = format_html_join('\n',
            '<div class="row"><div class="col-sm-12"><h4>{0}</h4></div></div>\n'
            '<div class="row"><div class="col-sm-12">{1}</div></div>\n'
            '<div class="row"><div class="col-sm-12"><small>{2}</small></div></div>\n',
            ((unicode(field.label), field.widget.render(field.name, values.get(field.name), attrs), unicode(field.help_text))
                for field in self.partial_fields)
        )
        return html


if DJANGO_VERSION[0] <= 1 and DJANGO_VERSION[1] <= 5:
    input_widget = widgets.TextInput
else:
    input_widget = widgets.NumberInput


class NumberInputWidget(input_widget):
    validation_pattern = re.compile('^\d+$')
    validation_message = _("In '%(label)s': Value '%(value)s' shall contain a valid number.")

    def validate(self, value):
        if not self.validation_pattern.match(value):
            raise ValidationError(self.validation_message, code='invalid', params={ 'value': value })


class MultipleTextInputWidget(widgets.MultiWidget):
    """
    A widgets accepting multiple input values to be used for rendering CSS inline styles.
    Additionally this widget validates the input data and raises a ValidationError
    """
    def __init__(self, labels, attrs=None):
        text_widgets = [widgets.TextInput({ 'placeholder': label }) for label in labels]
        super(MultipleTextInputWidget, self).__init__(text_widgets, attrs)
        self.labels = labels[:]
        self.validation_errors = []

    def __iter__(self):
        self.validation_errors = []
        for label in self.labels:
            yield label

    def decompress(self, values):
        if not isinstance(values, dict):
            values = {}
        for key in self.labels:
            values.setdefault(key, None)
        return values

    def value_from_datadict(self, data, files, name):
        values = {}
        for key in self.labels:
            values[key] = escape(data.get('{0}-{1}'.format(name, key)))
        return values

    def render(self, name, values, attrs):
        widgets = []
        values = values or {}
        for index, key in enumerate(self.labels):
            label = '{0}-{1}'.format(name, key)
            errors = key in self.validation_errors and 'errors' or ''
            widgets.append((self.widgets[index].render(label, values.get(key), attrs), errors))
        html = format_html('{0}', format_html_join('\n', '<div class="sibling-field {1}">{0}</div>', widgets))
        return html

    def validate(self, value, field_name):
        if hasattr(self, 'validation_pattern'):
            if not hasattr(self, 'validation_message'):
                raise AttributeError('Widget class is missing element validation_message')
            val = value.get(field_name)
            if val and not self.validation_pattern.match(val):
                self.validation_errors.append(field_name)
                raise ValidationError(self.validation_message, code='invalid', params={ 'value': val, 'field': field_name })


class MultipleNumberWidget(MultipleTextInputWidget):
    validation_pattern = re.compile('^\d+$')
    validation_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number.")


class MultipleInlineStylesWidget(MultipleTextInputWidget):
    validation_pattern = re.compile(r'^\d+(px|em|%)$')
    validation_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number, ending with px, em or %%.")
