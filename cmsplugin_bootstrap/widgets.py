# -*- coding: utf-8 -*-
import json
from django.forms import widgets
from django.utils.datastructures import SortedDict
from django.utils.html import escape, format_html, format_html_join
from django.utils.safestring import mark_safe

CSS_MARGIN_STYLES = ['margin-%s' % s for s in ('top', 'right', 'bottom', 'left')]
CSS_VERTICAL_SPACING = ['min-height']


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    def __init__(self, context_widgets):
        self.sorted_widgets = SortedDict(((item['key'], item) for item in context_widgets))
        if len(context_widgets) > len(self.sorted_widgets):
            raise AttributeError('List of context_widgets may contain only unique keys')
        super(JSONMultiWidget, self).__init__((item['widget'] for item in context_widgets))

    def decompress(self, value):
        values = json.loads(value or '{}')
        for key, item in self.sorted_widgets.items():
            if isinstance(item['widget'], widgets.MultiWidget):
                values[key] = item['widget'].decompress(values.get(key))
            else:
                values.setdefault(key, item.get('initial'))
        return values

    def value_from_datadict(self, data, files, name):
        result = {}
        for key, item in self.sorted_widgets.items():
            if isinstance(item['widget'], widgets.MultiWidget):
                result[key] = item['widget'].value_from_datadict(data, files, key)
            elif getattr(item['widget'], 'allow_multiple_selected', False):
                result[key] = map(escape, data.getlist(key))
            else:
                result[key] = escape(data.get(key))
        return result

    def render(self, name, value, attrs):
        values = self.decompress(value)
        html = format_html_join('',
            '<div class="row"><div class="col-sm-12"><h4>{0}</h4></div></div>'
            '<div class="row"><div class="col-sm-12">{1}</div></div>'
            '<div class="row"><div class="col-sm-12"><small>{2}</small></div></div>',
            ((unicode(item.get('label', '')), item['widget'].render(key, values.get(key), attrs), unicode(item.get('help_text', '')))
                for key, item in self.sorted_widgets.items())
        )
        return html


class MultipleTextInputWidget(widgets.MultiWidget):
    def __init__(self, labels, attrs={ 'class': 'sibling-field' }):
        text_widgets = [widgets.TextInput({ 'placeholder': label }) for label in labels]
        super(MultipleTextInputWidget, self).__init__(text_widgets, attrs)
        self.labels = labels[:]

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
            widgets.append(self.widgets[index].render(label, values.get(key), self.attrs))
        html = format_html('{0}', mark_safe(''.join(widgets)))
        return html
