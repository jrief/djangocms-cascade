import re
import json
from html.parser import HTMLParser  # py3

import warnings

from django.core.exceptions import ValidationError
from django.contrib.staticfiles.finders import find
from django.forms import Media, widgets
from django.utils.html import escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _, ugettext
from urllib.parse import quote, urlparse

from .fields import GlossaryField
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField
from cms.models import Page


class JSONMultiWidget(widgets.MultiWidget):
    """
    Deprecated.
    Base class for MultiWidgets using a JSON field in database.
    """
    html_parser = HTMLParser()

    def __init__(self, glossary_fields):
        from cmsplugin_cascade.fields import GlossaryField
        warnings.warn("JSONMultiWidget is deprecated")

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
        super().__init__((field.widget for field in self.normalized_fields))

    def decompress(self, values):
        if not isinstance(values, dict):
            values = json.loads(values or '{}')
        for field in self.normalized_fields:
            initial_value = field.initial() if callable(field.initial) else field.initial
            if isinstance(field.widget, widgets.MultiWidget):
                values[field.name] = field.widget.decompress(values.get(field.name, initial_value))
            else:
                values.setdefault(field.name, initial_value)
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

    def render(self, name, value, attrs=None, renderer=None):
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
                if isinstance(field_value, str):
                    field_value = self.html_parser.unescape(field_value)
                render_fields.append((
                    field.name,
                    str(field.label),
                    field.widget.render(field.name, field_value, field_attrs),
                    str(field.help_text),
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


class AColorPickerMixin(object):
    acolorpicker_js = 'node_modules/a-color-picker/dist/acolorpicker.js'

    def __init__(self, with_alpha, *args, **kwargs):
        self.with_acolorpicker = bool(find(self.acolorpicker_js))
        if with_alpha and not self.with_acolorpicker:
            msg = "Node package 'a-color-picker' not found in 'node_modules'.\n" \
                  "Please install it from npm into your project directory and add " \
                  "('node_modules', 'project_directory/node_modules') to your STATICFILES_DIRS."
            raise FileNotFoundError(msg)
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        if self.with_acolorpicker:
            js = [self.acolorpicker_js, 'cascade/js/admin/colorpicker.js']
        else:
            js = ['cascade/js/admin/colorpicker.js']
        return Media(js=js)

    @classmethod
    def rgb2hex(cls, val):
        match = re.search('rgb[a]?\((\d+),\s*(\d+),\s*(\d+)[^)]*\)', val)
        if match:
            val = "#{:02x}{:02x}{:02x}".format(*[int(m) for m in match.groups()])
        return val


class ColorPickerWidget(AColorPickerMixin, widgets.MultiWidget):
    """
    Use this field to enter a color value. Clicking onto this widget will pop up a color picker.
    The value passed to the consumer is a tuple of a Boolean and a string guaranteed to be in #rgb format.
    """
    template_name = 'cascade/admin/widgets/colorpicker.html'

    def __init__(self, with_alpha):
        widget_list = [
            widgets.TextInput(attrs={'data-with_alpha': str(with_alpha).lower(), 'class': 'cascade-rgba'}),
            widgets.TextInput(attrs={'type': 'color'}),
            widgets.CheckboxInput(),
        ]
        super().__init__(with_alpha, widget_list)

    @property
    def media(self):
        return super().media + Media(css={'all': ['cascade/css/admin/colorpicker.css']})

    def decompress(self, values):
        assert isinstance(values, (list, tuple)), "Values to decompress are kept as lists in JSON"
        values = list(values)
        return values

    def value_from_datadict(self, data, files, name):
        if self.with_acolorpicker:
            color = data.get('{}_0'.format(name))
        else:
            color = data.get('{}_1'.format(name))
        values = [
            escape(color),
            bool(data.get('{}_2'.format(name))),
        ]
        return values

    def get_context(self, name, value, attrs):
        if not isinstance(value, list):
            values = self.decompress(value)
        else:
            values = list(value)
        assert len(values) == 2
        values.insert(0, values[0])
        values[1] = self.rgb2hex(values[0])
        context = super().get_context(name, values, attrs)
        return context


class MultipleTextInputWidget(widgets.MultiWidget):
    """
    A widgets accepting multiple input values.
    """
    required = False

    def __init__(self, labels, attrs=None):
        text_widgets = [widgets.TextInput()] * len(labels)
        super().__init__(text_widgets, attrs)
        self.labels = labels[:]

    def decompress(self, values):
        assert isinstance(values, dict), "Values to decompress are kept as dict in JSON"
        return list(values.values())

    def value_from_datadict(self, data, files, name):
        values = [escape(data.get('{0}-{1}'.format(name, label), '')) for label in self.labels]
        return values

    def render(self, name, value, attrs=None, renderer=None):
        widgets = []
        values = value[:] if isinstance(value, (list, tuple)) else []
        values.extend([''] * max(len(self.labels) - len(values), 0))
        elem_id = attrs['id']
        for index, key in enumerate(self.labels):
            label = '{0}-{1}'.format(name, key)
            attrs['id'] = '{0}_{1}'.format(elem_id, key)
            widgets.append((self.widgets[index].render(label, values[index], attrs, renderer), key, label))
        return format_html('<div>{0}</div>',
                           format_html_join('\n',
                                            '<div class="sibling-field"><label for="{2}">{1}</label>{0}</div>',
                                            widgets))


class BorderChoiceWidget(AColorPickerMixin, widgets.MultiWidget):
    """
    Use this field to enter the three values of a border: width style color.
    """
    template_name = 'cascade/admin/widgets/borderchoice.html'

    def __init__(self, choices, with_alpha):
        widget_list = [
            widgets.TextInput(attrs={'size': 5}),
            widgets.Select(choices=choices),
            widgets.TextInput(attrs={'data-with_alpha': str(with_alpha).lower(), 'class': 'cascade-rgba'}),
            widgets.TextInput(attrs={'type': 'color'}),
        ]
        super().__init__(with_alpha, widget_list)

    @property
    def media(self):
        return super().media + Media(css={'all': ['cascade/css/admin/colorpicker.css',
                                                  'cascade/css/admin/borderchoice.css']})

    def decompress(self, values):
        assert isinstance(values, (list, tuple)), "Values to decompress are kept as lists in JSON"
        return list(values)

    def value_from_datadict(self, data, files, name):
        try:
            if self.with_acolorpicker:
                color = data.get('{}_2'.format(name))
            else:
                color = data.get('{}_3'.format(name))
            values = [
                escape(data['{}_0'.format(name)]),
                escape(data['{}_1'.format(name)]),
                escape(color),
            ]
        except KeyError:
            values = ['0px', 'none', 'none']
        return values

    def get_context(self, name, value, attrs):
        if not isinstance(value, list):
            values = self.decompress(value)
        else:
            values = list(value)
        assert len(values) == 3
        values.insert(2, values[2])
        values[3] = self.rgb2hex(values[2])
        context = super().get_context(name, values, attrs)
        return context

class HmltAttrsWidget(widgets.MultiWidget):
    """
    Use this field to enter a html attributes value.
    The value passed to the GlossaryField is guaranteed to be validate text, int and color format.
    Class HmltAttrsWidget has pre-set widget which can be entered in the settings file: 
    widget_choices_cms_page_anchors, widget_choices_list, widget_choices_int, widget_choices_text,
    widget_choices_color, widget_attrs.
    This class is made to work in conjunction with the Class ExtraFieldsMixin preferably.
    """
    DEFAULT_ATTRS = {'style': 'padding-left: 26px;'}
    invalid_message = _("In '%(label)s': Value '%(value)s' is not a valid.")
    validation_pattern = re.compile(r'^[A-Za-z0-9_-]+$')
    int_validation_pattern = re.compile(r'^[-+]?[0-9]+$')
    color_validation_pattern = re.compile('^#[0-9a-f]{3}([0-9a-f]{3})?$')
    all_extra_html_tag_attributes = {}

    def __init__(self, attrs=DEFAULT_ATTRS):
        attrs = dict(attrs)
        self.list_attrs_name = self.attributes_extra.keys() if hasattr(self, 'attributes_extra') else None
        widget_list = []
        for key, val in self.attributes_extra.items():
            self.all_extra_html_tag_attributes[self.widget_name] = self.attributes_extra
            choices = []
            if 'widget_attrs' in val:
                widgetattrs = val['widget_attrs']
                widgetattrs.update(attrs)
            if 'widget_choices_list' in val:
                attrs_add = {'style': 'width: 10em;'}
                widgetattrs.update(attrs_add)
                choices = val['widget_choices_list']
                widget_list.append(widgets.Select(attrs=widgetattrs, choices=[(s, s) for s in choices]))
            elif 'widget_choices_cms_page_anchors' in val :
                attrs_add = {'style': 'width: 10em;'}
                widgetattrs.update(attrs_add)
                if  hasattr(Page.objects.get(pk=self.current_page.pk), 'cascadepage'):
                     cascade_page = Page.objects.get(pk=self.current_page.pk).cascadepage
                     for cascade_id, cascade_id_value in cascade_page.glossary.get('element_ids', {}).items():
                         cascade_id_value='#{}'.format(cascade_id_value)
                         choices = [('inherit',_("Inherit")) , (cascade_id, cascade_id_value)]
                else:
                    choices = [('inherit',_("Inherit"))] 
                widget_list.append(widgets.Select(attrs=widgetattrs, choices=[s for s in choices]))
            elif 'widget_choices_int' in val:
                attrs_add = {'style': 'width: 9em;', 'type': 'text'}
                widgetattrs.update(attrs_add)
                widget_list.append(widgets.TextInput(attrs=widgetattrs))
            elif 'widget_choices_text' in val:
                attrs_add = {'style': 'width: 9em;', 'type': 'text'}
                widgetattrs.update(attrs_add)
                widget_list.append(widgets.TextInput(attrs=widgetattrs))
            elif 'widget_choices_color' in val:
                attrs_add = {'style': 'width: 10em;', 'type': 'color'}
                widgetattrs.update(attrs_add)
                widget_list.append(widgets.TextInput(attrs=widgetattrs))
        super(HmltAttrsWidget, self).__init__(widget_list)

    def __iter__(self):
        for name in self.list_attrs_name:
            yield name

    def decompress(self, values):
        if not isinstance(values, (list, tuple, dict)):
            values = {}
            for attr_name in self.list_attrs_name:
                values[attr_name] = ''
        return values

    def value_from_datadict(self, data, files, name):
        self.widgetname = name.split(':')[-1]
        values = {}
        for attr_name in self.list_attrs_name:
            data_attr = escape(data.get('{0}_{1}'.format(name, attr_name),''))
            if data_attr == 'inherit' or  data_attr == 'None':
                data_attr = ""
            values[attr_name] = data_attr
        return values

    def render(self, name, values, attrs):
        values = values
        attrs = dict(attrs)
        html = '<div class="clearfix">'
        html += '<div style="position: relative;">'
        if isinstance(values, dict):
            for index, attr_data_set in enumerate(values.items(), start=0):
                attribute_name = attr_data_set[0]
                attribute_values = attr_data_set[1]
                subkey = '{0}_{1}'.format(name, attribute_name)
                widget_attrs=[]
                if 'widget_attrs' in attribute_values:
                    widget_attrs = attribute_values['widget_attrs']
                html += format_html('<div style="float: left; width: 12em;" ><label for="{0}"><p>{1}</p>{2}</label></div>',
                           subkey, attribute_name , self.widgets[index].render(subkey, attribute_values, attrs ), widget_attrs)
        html += '</div></div>'
        return mark_safe(html)

    def validate(self, values, key):
        for index, v in enumerate(values.items(), start=0):
            key_attibute_name = v[0]
            value_attibute_value = v[1]
            if value_attibute_value != '':
                self.widgets[index].validate=True
                values_extra_attr = self.all_extra_html_tag_attributes.get(self.widgetname, '').get( key_attibute_name, '')
                if values_extra_attr:
                    if 'widget_choices_int' in values_extra_attr:
                        if not self.int_validation_pattern.match(value_attibute_value):
                            self.widgets[index].validate( value_attibute_value)
                            raise ValidationError(self.invalid_message, code='invalid', params={key_attibute_name : value_attibute_value})
                    elif 'widget_choices_color' in values_extra_attr:
                        if not self.color_validation_pattern.match(value_attibute_value):
                            self.widgets[index].validate(value_attibute_value)
                            raise ValidationError(self.invalid_message, code='invalid', params={key_attibute_name : value_attibute_value})
                    elif not self.validation_pattern.match(value_attibute_value):
                        self.widgets[index].validate(value_attibute_value)
                        raise ValidationError(self.invalid_message, code='invalid', params={key_attibute_name : value_attibute_value})