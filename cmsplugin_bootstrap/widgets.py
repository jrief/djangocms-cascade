# -*- coding: utf-8 -*-
import re
import json
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

    def decompress(self, value):
        values = json.loads(value or '{}')
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
        if not isinstance(values, dict):
            values = self.decompress(values)
        html = format_html_join('\n',
            '<div class="row"><div class="col-sm-12"><h4>{0}</h4></div></div>\n'
            '<div class="row"><div class="col-sm-12">{1}</div></div>\n'
            '<div class="row"><div class="col-sm-12"><small>{2}</small></div></div>\n',
            ((unicode(field.label), field.widget.render(field.name, values.get(field.name), attrs), unicode(field.help_text))
                for field in self.partial_fields)
        )
        return html


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
        for index, key in enumerate(self.labels):
            label = '{0}-{1}'.format(name, key)
            errors = key in self.validation_errors and 'errors' or ''
            widgets.append((self.widgets[index].render(label, values.get(key), attrs), errors))
        html = format_html('{0}', format_html_join('\n', '<div class="sibling-field {1}">{0}</div>', widgets))
        return html


class MultipleInlineStylesWidget(MultipleTextInputWidget):
    message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain only a number, ending with px or em.")
    prog = re.compile('^\d+(px|em)$')

    def __init__(self):
        super(MultipleInlineStylesWidget, self).__init__(CSS_MARGIN_STYLES + CSS_VERTICAL_SPACING)

    def validate(self, value, field_name):
        val = value.get(field_name)
        if val and not self.prog.match(val):
            self.validation_errors.append(field_name)
            raise ValidationError(self.message, code='invalid', params={ 'value': val, 'field': field_name })
