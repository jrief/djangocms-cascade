import re
import json
from django.core.exceptions import ValidationError
from django.forms import Media, widgets
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html, format_html_join
from six.moves.html_parser import HTMLParser
from django.utils.translation import ugettext_lazy as _, ugettext


class JSONMultiWidget(widgets.MultiWidget):
    """Base class for MultiWidgets using a JSON field in database"""
    html_parser = HTMLParser()

    def __init__(self, glossary_fields):
        from cmsplugin_cascade.fields import GlossaryField

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


class CascadingSizeWidgetMixin(object):
    POSSIBLE_UNITS = ('rem', 'px', 'em', '%')
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


class InheritCheckboxWidget(widgets.CheckboxInput):
    template_name = 'cascade/admin/widgets/inherit_color.html'


class ColorPickerWidget(widgets.MultiWidget):
    """
    Use this field to enter a color value. Clicking onto this widget will pop up a color picker.
    The value passed to the GlossaryField is guaranteed to be in #rgb format.
    """
    DEFAULT_ATTRS = {'type': 'color'}

    def __init__(self, with_alpha, attrs=DEFAULT_ATTRS):
        self.with_alpha = with_alpha
        attrs = dict(attrs)
        widget_list = [
            widgets.TextInput(attrs=attrs),
            InheritCheckboxWidget(),
        ]
        super(ColorPickerWidget, self).__init__(widget_list)

    @property
    def media(self):
        if self.with_alpha:
            js = ['cascade/js/admin/colorpickerext.js' ]
        else:
            js = ['cascade/js/admin/colorpicker.js' ]
        return Media(js=js)

    def __iter__(self):
        yield 'color'
        yield 'disabled'

    def decompress(self, values):
        assert isinstance(values, (list, tuple)), "Values to decompress are kept as lists in JSON"
        return list(values)

    def value_from_datadict(self, data, files, name):
        values = (
            escape(data.get('{}_0'.format(name))),
            bool(data.get('{}_1'.format(name))),
        )
        return values


class MultipleTextInputWidget(widgets.MultiWidget):
    """
    A widgets accepting multiple input values.
    """
    required = False

    def __init__(self, labels, attrs=None):
        text_widgets = [widgets.TextInput()] * len(labels)
        super().__init__(text_widgets, attrs)
        self.labels = labels[:]

    def __iter__(self):
        for label in self.labels:
            yield label

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


class MultipleCascadingSizeWidget(CascadingSizeWidgetMixin, MultipleTextInputWidget):
    """deprecated"""
    DEFAULT_ATTRS = {'style': 'width: 4em;'}
    invalid_message = _("In '%(label)s': Value '%(value)s' for field '%(field)s' shall contain a valid number, ending in %(endings)s.")

    def __init__(self, labels, allowed_units=None, attrs=None):
        if attrs is None:
            attrs = self.DEFAULT_ATTRS
        self.validation_pattern, self.invalid_message = self.compile_validation_pattern(
            units=allowed_units)
        super().__init__(labels, attrs=attrs)


class BorderChoiceWidget(widgets.MultiWidget):
    """
    Use this field to enter the three values of a border: width style color.
    """
    def __init__(self, choices):
        widget_list = [
            widgets.TextInput,
            widgets.Select(choices=choices),
            widgets.TextInput(attrs={'type': 'color'})
        ]
        super().__init__(widget_list)

    def decompress(self, values):
        assert isinstance(values, (list, tuple)), "Values to decompress are kept as lists in JSON"
        return list(values)

    def value_from_datadict(self, data, files, name):
        values = (
            escape(data['{0}-width'.format(name)]),
            escape(data['{0}-style'.format(name)]),
            escape(data['{0}-color'.format(name)]),
        )
        return values

    def render(self, name, value, attrs=None, renderer=None):
        elem_id = attrs['id']
        attrs = dict(attrs)
        parts = []
        for key, val, widget in zip(['width', 'style', 'color'], value, self.widgets):
            prop = '{0}-{1}'.format(name, key)
            attrs['id'] = '{0}_{1}'.format(elem_id, key)
            parts.append([widget.render(prop, val, attrs, renderer)])
        return format_html('<div>{0}</div>', format_html_join('', '<div class="sibling-field">{0}</div>', parts))
