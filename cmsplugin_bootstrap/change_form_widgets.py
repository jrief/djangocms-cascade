from django.forms import widgets
from django.utils import simplejson as json
from django.utils.safestring import mark_safe


class ExtraStylesWidget(widgets.MultiWidget):
    def __init__(self, styles):
        margin_widgets = [widgets.TextInput({ 'placeholder': s }) for s in styles]
        super(ExtraStylesWidget, self).__init__(margin_widgets)
        self.styles = styles[:]

    def decompress(self, value):
        values = value and json.loads(value) or {}
        for style in self.styles:
            values.setdefault(style, None)
        return values

    def value_from_datadict(self, data, files, name):
        result = dict((s, data.get(s) or None) for s in self.styles)
        return result

    def render(self, name, value, attrs=None):
        values = self.decompress(value)
        html = '<div class="clearfix">'
        for k, style in enumerate(self.styles):
            html += self.widgets[k].render(style, values.get(style), attrs)
        html += '</div>'
        return mark_safe(html)


class MultipleRadioButtonsWidget(widgets.MultiWidget):
    def __init__(self, widgets_choices):
        """
        Creates one or more independent rows of radio button widgets, each of which declares its own
        choices. widget_choices shall be a tuple of tuples containing the name followed by a tuple
        of two-choices of choices.
        """
        if not widgets_choices or not isinstance(widgets_choices, (list, tuple)) or not isinstance(widgets_choices[0], tuple):
            raise AttributeError('widgets_choices must be list or tuple of tuples')
        self.prefixes = []
        option_widgets = []
        for prefix, choices in widgets_choices:
            self.prefixes.append(prefix)
            option_widgets.append(widgets.RadioSelect(choices=choices))
        super(MultipleRadioButtonsWidget, self).__init__(option_widgets)

    def decompress(self, value):
        values = value and json.loads(value) or []
        values += [None] * (len(self.prefixes) - len(values))
        return values

    def value_from_datadict(self, data, files, name):
        return [data.get(prefix) for prefix in self.prefixes]

    def render(self, name, value, attrs=None):
        value = self.decompress(value)
        html = '<div class="radio-row">'
        for index, prefix in enumerate(self.prefixes):
            html += self.widgets[index].render(prefix, value[index], attrs)
        html += '</div>'
        return mark_safe(html)


class MultipleCheckboxesWidget(widgets.CheckboxSelectMultiple):
    def __init__(self, choices):
        """
        Creates one or more independent rows of radio button widgets, each of which declares its own
        choices. widget_choices shall be a tuple of tuples containing the name followed by a tuple
        of two-choices of choices.
        """
        if not choices or not isinstance(choices, tuple):
            raise AttributeError('choices must be list or tuple of tuples')
        self.labels = [c for c, _ in choices]
        super(MultipleCheckboxesWidget, self).__init__(choices=choices)

    def render(self, name, value, attrs=None):
        values = value and json.loads(value) or []
        values += [None] * (len(self.labels) - len(values))
        html = '<div class="checkboxes-row">'
        html += super(MultipleCheckboxesWidget, self).render(name, values, attrs)
        html += '</div>'
        return mark_safe(html)
