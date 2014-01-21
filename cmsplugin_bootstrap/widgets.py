# -*- coding: utf-8 -*-
import json
from django.forms import widgets
from django.utils.datastructures import SortedDict
from django.utils.html import format_html, format_html_join


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def __init__(self, data_widgets):
        if len(data_widgets) > len(set((item['key'] for item in data_widgets))):
            raise AttributeError('List of data_widgets must contain only unique keys')
        self.prefixes = SortedDict(((item['key'], item.get('initial')) for item in data_widgets))
        super(JSONMultiWidget, self).__init__((item['widget'] for item in data_widgets))

    def decompress(self, value):
        values = json.loads(value or '{}')
        for prefix, initial in self.prefixes.items():
            values.setdefault(prefix, initial)
        return values

    def value_from_datadict(self, data, files, name):
        def get_data(prefix, widget):
            if getattr(widget, 'allow_multiple_selected', False):
                return data.getlist(prefix)
            return data.get(prefix)

        result = dict((p, get_data(p, w)) for p, w in zip(self.prefixes.keys(), self.widgets))
        return result

    def render(self, name, value, attrs=None):
        values = self.decompress(value)
        html = format_html_join('', '<div class="multi-widget-row">{0}</div>',
            ((self.widgets[index].render(prefix, values.get(prefix), attrs),) for index, prefix in enumerate(self.prefixes.keys()))
        )
        return html


class MultipleCheckboxesWidget(widgets.CheckboxSelectMultiple):
    """
    Creates one row of checkbox widgets.
    """
#     def __init__(self, choices):
#         if not choices or not isinstance(choices, (list, tuple)) or not isinstance(choices[0], tuple):
#             raise AttributeError('choices must be list or tuple of tuples')
#         super(MultipleCheckboxesWidget, self).__init__(choices=choices)
#         #self.labels = [choice[0] for choice in choices]

    def render(self, name, value, attrs=None):
        html = format_html('<div class="multi-widget-row">{0}</div>',
                    super(MultipleCheckboxesWidget, self).render(name, value, attrs))
        return html
