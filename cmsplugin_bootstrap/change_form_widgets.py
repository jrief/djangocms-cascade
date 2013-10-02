from django.forms import widgets
from django.utils import simplejson as json
from django.utils.safestring import mark_safe
from cmsplugin_bootstrap.models import CSS_STYLE_DIRS


class ExtraStylesWidget(widgets.MultiWidget):
    def __init__(self, **kwargs):
        wdg_attrs = [{ 'placeholder': 'margin-%s' % d, 'class': 'style-field' } for d in CSS_STYLE_DIRS]
        margin_widgets = [widgets.TextInput(m) for m in wdg_attrs]
        super(ExtraStylesWidget, self).__init__(margin_widgets)

    def decompress(self, value):
        value = value and json.loads(value) or []
        value += [None] * (len(CSS_STYLE_DIRS) - len(value))
        return value

    def value_from_datadict(self, data, files, name):
        result = [data.get('margin-%s' % d) or None for d in CSS_STYLE_DIRS]
        return result

    def render(self, name, value, attrs=None):
        values = self.decompress(value)
        html = '<div class="clearfix">'
        for k, d in enumerate(CSS_STYLE_DIRS):
            html += self.widgets[k].render('margin-%s' % d, values[k], attrs)
        html += '</div>'
        return mark_safe(html)


class SingleOptionWidget(widgets.MultiWidget):
    def __init__(self, prefix, choices):
        self.prefix = prefix
        option_widgets = [widgets.RadioSelect(choices=choices)]
        super(SingleOptionWidget, self).__init__(option_widgets)

    def decompress(self, value):
        value = value and json.loads(value) or []
        value += [None] * (1 - len(value))
        return value

    def value_from_datadict(self, data, files, name):
        return [data.get(self.prefix)]

    def render(self, name, value, attrs=None):
        value = self.decompress(value)
        html = '<div class="clearfix">' + self.widgets[0].render(self.prefix, value[0], attrs) + '</div>'
        return mark_safe(html)
