# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import json
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _, ugettext
from .fields import GlossaryField


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    html_parser = HTMLParser()

    def __init__(self, glossary_fields):
        self.glossary_fields = list(glossary_fields)
        self.normalized_fields = []
        for field in self.glossary_fields:
            if isinstance(field, GlossaryField):
                self.normalized_fields.append(field)
            elif isinstance(field, (list, tuple)):
                self.normalized_fields.extend([f for f in field if isinstance(f, GlossaryField)])
            else:
                raise ValueError("Given fields must be of type GlossaryField or list of thereof")
        unique_keys = set([field.name for field in self.normalized_fields])
        if len(self.normalized_fields) > len(unique_keys):
            raise ValueError('List of glossary_fields may contain only unique keys')
        super(JSONMultiWidget, self).__init__((field.widget for field in self.normalized_fields))

    def decompress(self, values):
        while isinstance(values, str):
            values=json.loads(values)    
        if not isinstance(values, dict):
            values = json.loads(values or '{}')
        for field in self.normalized_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                values[field.name] = field.widget.decompress(values.get(field.name, field.initial))
            else:
                values.setdefault(field.name, field.initial)
        return values

    def value_from_datadict(self, data, files, name):
        result = {}
        for field in self.normalized_fields:
            if isinstance(field.widget, widgets.MultiWidget):
                result[field.name] = field.widget.value_from_datadict(data, files, field.name)
            elif getattr(field.widget, 'allow_multiple_selected', False):
                result[field.name] = list(map(escape, data.getlist(field.name)))
            else:
                result[field.name] = escape(data.get(field.name, ''))
        return result

    def value_omitted_from_data(self, data, files, name):
        # required since Django-1.10 during invocation of `construct_instance`
        return self.normalized_fields and all(
            field.widget.value_omitted_from_data(data, files, field.name)
            for field in self.normalized_fields
        )

    def render(self, name, value, attrs):
        values = self.decompress(value)
        render_fieldsets = []
        for fieldset in self.glossary_fields:
            render_fields = []
            if not isinstance(fieldset, (list, tuple)):
                fieldset = [fieldset]
            for field in fieldset:
                field_attrs = dict(**attrs)
                field_attrs.update(id='{id}_{0}'.format(field.name, **attrs))
                field_value = values.get(field.name)
                if isinstance(field_value, six.string_types):
                    field_value = self.html_parser.unescape(field_value)
                render_fields.append((
                    field.name,
                    six.text_type(field.label),
                    field.widget.render(field.name, field_value, field_attrs),
                    six.text_type(field.help_text),
                ))
            html = format_html_join('',
                 '<div class="glossary-field glossary_{0}"><h1>{1}</h1><div class="glossary-box">{2}</div><small>{3}</small></div>',
                 render_fields)
            render_fieldsets.append((html,))
        return format_html_join('\n', '<div class="glossary-widget">{0}</div>', render_fieldsets)


class NumberInputWidget(widgets.NumberInput):
    validation_pattern = re.compile('^-?\d+(\.\d{1,2})?$')
    required_message = _("In '%(label)s': This field is required.")
    invalid_message = _("In '%(label)s': Value '%(value)s' shall contain a valid decimal number.")

    def validate(self, value):
        if value and not self.validation_pattern.match(value):
            raise ValidationError(self.invalid_message, code='invalid', params={'value': value})


class CascadingSizeWidgetMixin(object):
    POSSIBLE_UNITS = ('px', 'em', '%')
    required_message = _("In '%(label)s': This field is required.")
    invalid_message = _("In '%(label)s': Value '%(value)s' shall contain a valid number, ending in %(endings)s.")

    def compile_validation_pattern(self, units=None):
        """
        Assure that passed in units are valid size units, or if missing, use all possible units.
        Return a tuple with a regular expression to be used for validating and an error message
        in case this validation failed.
        """
        if units is None:
            units = list(self.POSSIBLE_UNITS)
        else:
            for u in units:
                if u not in self.POSSIBLE_UNITS:
                    raise ValidationError('{} is not a valid unit for a size field'.format(u))
        regex = re.compile(r'^(-?\d+)({})$'.format('|'.join(units)))
        endings = (' %s ' % ugettext("or")).join("'%s'" % u.replace('%', '%%') for u in units)
        params = {'label': '%(label)s', 'value': '%(value)s', 'field': '%(field)s', 'endings': endings}
        return regex, self.invalid_message % params


class CascadingSizeWidget(CascadingSizeWidgetMixin, widgets.TextInput):
    """
    Use this field for validating Input Fields containing a value ending in ``px``, ``em`` or ``%``.
    Use it for values representing a margin, padding, width or height.
    """
    DEFAULT_ATTRS = {'style': 'width: 5em;'}

    def __init__(self, allowed_units=None, attrs=None, required=None):
        self.required = True if required is None else required
        if attrs is None:
            attrs = self.DEFAULT_ATTRS
        self.validation_pattern, self.invalid_message = self.compile_validation_pattern(
            units=allowed_units)
        super(CascadingSizeWidget, self).__init__(attrs=attrs)

    def validate(self, value):
        if not value:
            if self.required:
                raise ValidationError(self.required_message, code='required', params={})
            return
        if value == '0':
            return
        match = self.validation_pattern.match(value)
        if not (match and match.group(1).isdigit()):
            params = {'value': value}
            raise ValidationError(self.invalid_message, code='invalid', params=params)


class ColorPickerWidget(widgets.MultiWidget):
    """
    Use this field to enter a color value. Clicking onto this widget will pop up a color picker.
    The value passed to the GlossaryField is guaranteed to be in #rgb format.
    """
    DEFAULT_COLOR = '#ffffff'
    DEFAULT_ATTRS = {'style': 'width: 5em;', 'type': 'color'}
    validation_pattern = re.compile('^#[0-9a-f]{3}([0-9a-f]{3})?$')
    invalid_message = _("In '%(label)s': Value '%(value)s' is not a valid color.")

    def __init__(self, attrs=DEFAULT_ATTRS):
        attrs = dict(attrs)
        widget_list = [widgets.TextInput(attrs=attrs), widgets.CheckboxInput()]
        super(ColorPickerWidget, self).__init__(widget_list)

    def __iter__(self):
        for name in ('color', 'disabled'):
            yield name

    def decompress(self, values):
        if not isinstance(values, (list, tuple)) or len(values) != 2:
            # Disabled on
            values = ('on', self.DEFAULT_COLOR,)
        return values

    def value_from_datadict(self, data, files, name):
        values = (
            escape(data.get('{0}_disabled'.format(name), '')),
            escape(data.get('{0}_color'.format(name), self.DEFAULT_COLOR)),
        )
        return values

    def render(self, name, values, attrs):
        disabled, color = values
        elem_id = attrs['id']
        attrs = dict(attrs)
        html = '<div class="clearfix">'
        key, attrs['id'] = '{0}_color'.format(name), '{0}_color'.format(elem_id)
        html += format_html('<div class="sibling-field">{0}</div>', self.widgets[0].render(key, color, attrs))
        key, attrs['id'] = '{0}_disabled'.format(name), '{0}_disabled'.format(elem_id)
        html += format_html('<div class="sibling-field"><label for="{0}">{1}{2}</label></div>',
                            key, self.widgets[1].render(key, disabled, attrs), _("Inherit"))
        html += '</div>'
        return mark_safe(html)

    def validate(self, values, field_name):
        if field_name == 'color':
            color = values[1]
            if not self.validation_pattern.match(color):
                raise ValidationError(self.invalid_message, code='invalid', params={'value': color})


class SelectTextAlignWidget(widgets.Select):
    CHOICES = [('left', 'left'), ('center', 'center'), ('right', 'right'), ('justify', 'justify')]

    def __init__(self, attrs=None):
        super(SelectTextAlignWidget, self).__init__(attrs, choices=self.CHOICES)


class SelectOverflowWidget(widgets.Select):
    CHOICES = [('auto', 'auto'), ('scroll', 'scroll'), ('hidden', 'hidden')]

    def __init__(self, attrs=None):
        super(SelectOverflowWidget, self).__init__(attrs, choices=self.CHOICES)


class MultipleTextInputWidget(widgets.MultiWidget):
    """
    A widgets accepting multiple input values to be used for rendering CSS inline styles.
    Additionally this widget validates the input data and raises a ValidationError
    """
    required = False

    def __init__(self, labels, required=None, attrs=None):
        text_widgets = [widgets.TextInput({'placeholder': label}) for label in labels]
        super(MultipleTextInputWidget, self).__init__(text_widgets, attrs)
        self.labels = labels[:]
        if required is not None:
            self.required = required
        self.validation_errors = []
        # check if derived classes contain proper error messages
        if hasattr(self, 'validation_pattern') and not hasattr(self, 'invalid_message'):
            raise AttributeError("Multiple...InputWidget class is missing element: 'invalid_message'")
        if self.required and not hasattr(self, 'required_message'):
            raise AttributeError("Multiple...InputWidget class is missing element: 'required_message'")

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
            values[key] = escape(data.get('{0}-{1}'.format(name, key), ''))
        return values

    def render(self, name, value, attrs):
        widgets = []
        values = value or {}
        elem_id = attrs['id']
        for index, key in enumerate(self.labels):
            label = '{0}-{1}'.format(name, key)
            attrs['id'] = '{0}_{1}'.format(elem_id, key)
            errors = key in self.validation_errors and 'errors' or ''
            widgets.append((self.widgets[index].render(label, values.get(key), attrs), key, label, errors))
        return format_html('<div class="clearfix">{0}</div>',
                    format_html_join('\n', '<div class="sibling-field {3}"><label for="{2}">{1}</label>{0}</div>', widgets))

    def validate(self, value, field_name):
        if hasattr(self, 'validation_pattern'):
            val = value.get(field_name)
            if not val:
                if self.required:
                    raise ValidationError(self.required_message, code='required', params={'field': field_name})
                return
            if val and not self.validation_pattern.match(val):
                self.validation_errors.append(field_name)
                params = {'value': val, 'field': field_name}
                raise ValidationError(self.invalid_message, code='invalid', params=params)


class MultipleCascadingSizeWidget(CascadingSizeWidgetMixin, MultipleTextInputWidget):
    DEFAULT_ATTRS = {'style': 'width: 4em;'}
    invalid_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number, ending in %(endings)s.")

    def __init__(self, labels, allowed_units=None, attrs=None, required=True):
        if attrs is None:
            attrs = self.DEFAULT_ATTRS
        self.validation_pattern, self.invalid_message = self.compile_validation_pattern(
            units=allowed_units)
        super(MultipleCascadingSizeWidget, self).__init__(labels, required=required, attrs=attrs)


class SetBorderWidget(widgets.MultiWidget):
    """
    Use this field to enter the three values of a border: width style color.
    """
    DEFAULT_COLOR = '#000000'
    BORDER_STYLES = ['none', 'solid', 'dashed', 'dotted', 'double', 'groove', 'hidden',
                     'inset', 'outset', 'ridge']

    invalid_border_message = _("In '%(label)s': Value '%(value)s' is not a valid border style.")
    color_validation_pattern = re.compile('^#[0-9a-f]{3}([0-9a-f]{3})?$')
    invalid_color_message = _("In '%(label)s': Value '%(value)s' is not a valid color.")

    def __init__(self, attrs=None):
        widget_list = [
            CascadingSizeWidget(),
            widgets.Select(choices=[(s, s) for s in self.BORDER_STYLES]),
            widgets.TextInput(attrs={'style': 'width: 5em;', 'type': 'color'})
        ]
        super(SetBorderWidget, self).__init__(widget_list)

    def __iter__(self):
        for name in ('width', 'style', 'color'):
            yield name

    def decompress(self, values):
        if not isinstance(values, (list, tuple)) or len(values) != 3:
            values = ('0px', 'none', self.DEFAULT_COLOR,)
        return values

    def value_from_datadict(self, data, files, name):
        values = (
            escape(data.get('{0}-width'.format(name), '0px')),
            escape(data.get('{0}-style'.format(name), 'none')),
            escape(data.get('{0}-color'.format(name), self.DEFAULT_COLOR)),
        )
        return values

    def render(self, name, values, attrs):
        width, style, color = values
        elem_id = attrs['id']
        attrs = dict(attrs)
        html = '<div class="clearfix">'
        key, attrs['id'] = '{0}-width'.format(name), '{0}_width'.format(elem_id)
        html += format_html('<div class="sibling-field">{0}</div>', self.widgets[0].render(key, width, attrs))
        key, attrs['id'] = '{0}-style'.format(name), '{0}_style'.format(elem_id)
        html += format_html('<div class="sibling-field">{0}</div>', self.widgets[1].render(key, style, attrs))
        key, attrs['id'] = '{0}-color'.format(name), '{0}_color'.format(elem_id)
        html += format_html('<div class="sibling-field">{0}</div>', self.widgets[2].render(key, color, attrs))
        html += '</div>'
        return mark_safe(html)

    def validate(self, values, key):
        if key == 'width':
            if values[0]:
                self.widgets[0].validate(values[0])
        elif key == 'style':
            style = values[1]
            if style not in self.BORDER_STYLES:
                raise ValidationError(self.invalid_border_message, code='invalid', params={'value': style})
        elif key == 'color':
            color = values[2]
            if not self.color_validation_pattern.match(color):
                raise ValidationError(self.invalid_color_message, code='invalid', params={'value': color})
        else:
            raise KeyError("{} is not a valid border widget attribute.".format(key))
