# -*- coding: utf-8 -*-
import re
import six
import json
from django import VERSION as DJANGO_VERSION
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.html import escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def __init__(self, glossary_fields):
        unique_keys = set([field.name for field in glossary_fields])
        if len(glossary_fields) > len(unique_keys):
            raise AttributeError('List of glossary_fields may contain only unique keys')
        self.glossary_fields = glossary_fields[:]
        super(JSONMultiWidget, self).__init__((field.widget for field in glossary_fields))

    def decompress(self, values):
        if not isinstance(values, dict):
            values = json.loads(values or '{}')
        for field in self.glossary_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                values[field.name] = field.widget.decompress(values.get(field.name))
            else:
                values.setdefault(field.name, field.initial)
        return values

    def value_from_datadict(self, data, files, name):
        result = {}
        for field in self.glossary_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                result[field.name] = field.widget.value_from_datadict(data, files, field.name)
            elif getattr(field.widget, 'allow_multiple_selected', False):
                result[field.name] = list(map(escape, data.getlist(field.name)))
            else:
                result[field.name] = escape(data.get(field.name))
        return result

    def render(self, name, values, attrs):
        values = self.decompress(values)
        field_attrs = dict(**attrs)
        render_fields = []
        for field in self.glossary_fields:
            field_attrs['id'] = attrs['id'] + '_' + field.name
            render_fields.append((
                field.name,
                six.text_type(field.label),
                field.widget.render(field.name, values.get(field.name), field_attrs),
                six.text_type(field.help_text)
            ))
        html = format_html_join('\n',
            '<div class="glossary-widget glossary_{0}"><h1>{1}</h1><div class="glossary-box">{2}</div><small>{3}</small></div>',
            render_fields)
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
            raise ValidationError(self.validation_message, code='invalid', params={'value': value})


class CascadingSizeWidget(widgets.TextInput):
    """
    Use this field for validating Input Fields containing a value ending in ``px``, ``em`` or ``%``.
    Use it for values representing a margin, padding, width or height.
    """
    POSSIBLE_UNITS = ['px', 'em', '%']
    DEFAULT_ATTRS = {'style': 'width: 5em;'}

    def __init__(self, allowed_units=POSSIBLE_UNITS, attrs=DEFAULT_ATTRS, is_required=True, *args, **kwargs):
        for u in allowed_units:
            if u not in self.POSSIBLE_UNITS:
                raise ValidationError('{0} is not a valid unit for CascadingSizeField'.format(u))
        self.allowed_units = allowed_units
        self.validation_pattern = re.compile(r'^(\d+)\s*({0})$'.format('|'.join(allowed_units)))
        self.is_required = is_required
        super(CascadingSizeWidget, self).__init__(attrs=attrs, *args, **kwargs)

    def validate(self, value):
        if not value and self.is_required:
            raise ValidationError(_("In '%(label)s': This field is required."), params={})
        match = self.validation_pattern.match(value)
        if not (match and match.group(1).isdigit()):
            endings = _("or").join(" '%s' " % u for u in self.allowed_units)
            params = {'value': value, 'endings': endings}
            raise ValidationError(_("In '%(label)s': Value '%(value)s' shall contain a valid number, ending in%(endings)s."), params=params)


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
        return format_html('<div class="clearfix">{0}</div>',
                    format_html_join('\n', '<div class="sibling-field {1}">{0}</div>', widgets))

    def validate(self, value, field_name):
        if hasattr(self, 'validation_pattern'):
            if not hasattr(self, 'validation_message'):
                raise AttributeError("Widget class is missing element: 'validation_message'")
            val = value.get(field_name)
            if val and not self.validation_pattern.match(val):
                self.validation_errors.append(field_name)
                raise ValidationError(self.validation_message, code='invalid', params={'value': val, 'field': field_name})


class MultipleNumberWidget(MultipleTextInputWidget):
    validation_pattern = re.compile('^\d+$')
    validation_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number.")


class MultipleInlineStylesWidget(MultipleTextInputWidget):
    validation_pattern = re.compile(r'^\d+(px|em|%)$')
    validation_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number, ending with px, em or %%.")
