# -*- coding: utf-8 -*-
import json
from django.forms import widgets
from django.utils.safestring import mark_safe


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def decompress(self, value):
        values = value and json.loads(value) or {}
        for prefix in self.prefixes:
            values.setdefault(prefix, None)
        return values

    def value_from_datadict(self, data, files, name):
        result = dict((p, data.get(p) or None) for p in self.prefixes)
        return result

    def render(self, name, value, attrs=None):
        values = self.decompress(value)
        html = '<div class="multi-widget-row">'
        for index, prefix in enumerate(self.prefixes):
            html += self.widgets[index].render(prefix, values.get(prefix), attrs)
        html += '</div>'
        return mark_safe(html)


class ExtraStylesWidget(JSONMultiWidget):
    """
    Creates one or more independent text fields to keep extra styles applied to the
    corresponding HTML element.
    """
    def __init__(self, styles):
        margin_widgets = [widgets.TextInput({ 'placeholder': s }) for s in styles]
        super(ExtraStylesWidget, self).__init__(margin_widgets)
        self.prefixes = styles[:]


class MultipleRadioButtonsWidget(JSONMultiWidget):
    """
    Creates one or more independent rows of radio button widgets, each of which declares its own
    choices. widget_choices shall be a tuple of tuples containing the name followed by a tuple
    of two-choices of choices.
    """
    def __init__(self, choices):
        if not choices or not isinstance(choices, (list, tuple)) or not isinstance(choices[0], tuple):
            raise AttributeError('choices must be list or tuple of tuples')
        radio_widgets = dict((key, widgets.RadioSelect(choices=ch)) for key, ch in choices)
        super(MultipleRadioButtonsWidget, self).__init__(radio_widgets.values())
        self.prefixes = radio_widgets.keys()


class MultipleCheckboxesWidget(widgets.CheckboxSelectMultiple):
    """
    Creates one or more independent rows of radio button widgets, each of which declares its own
    choices. widget_choices shall be a tuple of tuples containing the name followed by a tuple
    of two-choices of choices.
    """
    def __init__(self, choices):
        if not choices or not isinstance(choices, (list, tuple)) or not isinstance(choices[0], tuple):
            raise AttributeError('choices must be list or tuple of tuples')
        super(MultipleCheckboxesWidget, self).__init__(choices=choices)
        self.labels = [choice[0] for choice in choices]

    def render(self, name, value, attrs=None):
        values = value and json.loads(value) or []
        values += [None] * (len(self.labels) - len(values))
        html = '<div class="multi-widget-row">'
        html += super(MultipleCheckboxesWidget, self).render(name, values, attrs)
        html += '</div>'
        return mark_safe(html)
