# -*- coding: utf-8 -*-
import json
from django.forms import widgets
from django.utils.datastructures import SortedDict
from django.utils.html import escape, format_html, format_html_join

CSS_MARGIN_STYLES = ['margin-%s' % s for s in ('top', 'right', 'bottom', 'left')]


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def __init__(self, data_widgets):
        if len(data_widgets) > len(set((item['key'] for item in data_widgets))):
            raise AttributeError('List of data_widgets may contain only unique keys')
        #self.prefixes = SortedDict(((item['key'], item.get('initial')) for item in data_widgets))
        self.prefixes = [item['key'] for item in data_widgets]
        self.data_widgets = data_widgets[:]
        super(JSONMultiWidget, self).__init__((item['widget'] for item in data_widgets))

    def decompress(self, value):
        values = json.loads(value or '{}')
        for item in self.data_widgets:
            values.setdefault(item['key'], item.get('initial'))
        return values

    def value_from_datadict(self, data, files, name):
        def get_data(prefix, widget):
            if getattr(widget, 'allow_multiple_selected', False):
                return map(escape, data.getlist(prefix))
            return escape(data.get(prefix))

        result = dict((p, get_data(p, w)) for p, w in zip(self.prefixes, self.widgets))
        return result

    def render(self, name, value, attrs):
        values = self.decompress(value)
        html = format_html_join('', '<div class="row">{0}</div>',
            ((self.widgets[index].render(prefix, values.get(prefix), attrs), )
                for index, prefix in enumerate(self.prefixes))
        )
        return html


class MultipleCheckboxesWidget(widgets.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None):
        html = format_html('<div class="col-sm-12">{0}</div>',
                    super(MultipleCheckboxesWidget, self).render(name, value, attrs))
        return html


class MultipleTextInputWidget(widgets.MultiWidget):
    def __init__(self, text_fields, attrs=None):
        text_widgets = [widgets.TextInput({ 'placeholder': field }) for field in text_fields]
        super(MultipleTextInputWidget, self).__init__(text_widgets, attrs)
        self.text_fields = text_fields[:]

    def decompress(self, value):
        values = value or {}
        for prefix in self.text_fields:
            values.setdefault(prefix, None)
        return values

    def value_from_datadict(self, data, files, name):
        raise Exception('Not implemented')

    def render(self, name, value, attrs):
        values = self.decompress(value)
        html = format_html('<div class="col-sm-12">{0}</div>',
            format_html_join('', '{0}',
                ((self.widgets[index].render(prefix, values.get(prefix), self.attrs),)
                    for index, prefix in enumerate(self.text_fields))
        ))
        return html
