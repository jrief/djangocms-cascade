import re
import warnings
from django.forms import widgets
from django.forms.fields import Field, CharField, ChoiceField, BooleanField, MultiValueField
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from django.core.validators import ProhibitNullCharactersValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _, ugettext
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.widgets import ColorPickerWidget, BorderChoiceWidget


class GlossaryField(object):
    """
    Deprecated.
    Behave similar to django.forms.Field, encapsulating a partial dictionary, stored as
    JSONField in the database.
    """
    def __init__(self, widget, label=None, name=None, initial='', help_text='', error_class=ErrorList):
        warnings.warn("GlossaryField is deprecated")
        self.name = name
        if not isinstance(widget, widgets.Widget):
            raise AttributeError('`widget` must inherit from django.forms.widgets.Widget')
        if label is None:
            label = name
        self.widget = widget
        self.label = label
        self.initial = initial
        self.help_text = help_text
        self.error_class = error_class

    def run_validators(self, value):
        if not callable(getattr(self.widget, 'validate', None)):
            return
        errors = []
        if callable(getattr(self.widget, '__iter__', None)):
            for field_name in self.widget:
                try:
                    self.widget.validate(value.get(self.name), field_name)
                except ValidationError as e:
                    if isinstance(getattr(e, 'params', None), dict):
                        e.params.update(label=self.label)
                    messages = self.error_class([m for m in e.messages])
                    errors.extend(messages)
        else:
            try:
                self.widget.validate(value.get(self.name))
            except ValidationError as e:
                if isinstance(getattr(e, 'params', None), dict):
                    e.params.update(label=self.label)
                errors = self.error_class([m for m in e.messages])
        if errors:
            raise ValidationError(errors)

    def get_element_ids(self, prefix_id):
        """
        Returns a single or a list of element ids, one for each input widget of this field
        """
        if isinstance(self.widget, widgets.MultiWidget):
            ids = ['{0}_{1}_{2}'.format(prefix_id, self.name, field_name) for field_name in self.widget]
        elif isinstance(self.widget, (widgets.SelectMultiple, widgets.RadioSelect)):
            ids = ['{0}_{1}_{2}'.format(prefix_id, self.name, k) for k in range(len(self.widget.choices))]
        else:
            ids = ['{0}_{1}'.format(prefix_id, self.name)]
        return ids



class BorderChoiceField(MultiValueField):
    BORDER_STYLES = ['none', 'solid', 'dashed', 'dotted', 'double', 'groove', 'hidden',
                     'inset', 'outset', 'ridge']

    def __init__(self, *args, **kwargs):
        choices = [(s, s) for s in self.BORDER_STYLES]
        widget = kwargs.pop('widget', BorderChoiceWidget(choices))
        fields = [
            SizeField(),
            ChoiceField(choices=choices),
            CharField(),
        ]
        kwargs['initial'] = ['0px', 'none', '#000000']
        super().__init__(fields=fields, widget=widget, *args, **kwargs)

    def prepare_value(self, value):
        return value

    def compress(self, data_list):
        return data_list


@deconstructible
class ColorValidator():
    message = _("'%(color)s' is not a valid color code. ")
    code = 'invalid_color_code'

    def __init__(self, with_alpha):
        self.with_alpha = with_alpha
        if self.with_alpha:
            self.validation_pattern = re.compile(r'(#(?:[0-9a-fA-F]{2}){2,4}|(#[0-9a-fA-F]{3})|(rgb|hsl)a?\((-?\d+%?[,\s]+){2,3}\s*[\d\.]+%?\))')
        else:
            self.validation_pattern = re.compile(r'(#(?:[0-9a-fA-F]{2}){2,3}|(#[0-9a-fA-F]{3})|(rgb|hsl))')

    def __call__(self, value):
        inherit, color = value
        match = self.validation_pattern.match(color)
        if not (isinstance(inherit, bool) and match):
            params = {'color': color}
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.with_alpha == other.with_alpha and
            self.message == other.message and
            self.code == other.code
        )


class ColorField(MultiValueField):
    DEFAULT_COLOR = '#ffffff'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        inherit_color = kwargs.pop('inherit_color', False)
        default_color = kwargs.pop('default_color', self.DEFAULT_COLOR)
        with_alpha = kwargs.pop('with_alpha', app_settings.CMSPLUGIN_CASCADE['color_picker_with_alpha'])
        widget = kwargs.pop('widget', ColorPickerWidget(with_alpha))
        fields = [
            CharField(initial=default_color),
            BooleanField(initial=inherit_color),
        ]
        kwargs['initial'] = [default_color, inherit_color]
        super().__init__(fields=fields, widget=widget, *args, **kwargs)
        self.validators.append(ColorValidator(with_alpha))
        self.validators.append(ProhibitNullCharactersValidator())

    def prepare_value(self, value):
        """
        Swap 'color' and 'inherit' for backward compatibility
        """
        inherit, color = value
        return color, inherit

    def compress(self, data_list):
        """
        Swap 'color' and 'inherit' for backward compatibility
        """
        return data_list[1], data_list[0]


@deconstructible
class SizeUnitValidator():
    allowed_units = []
    message = _("'%(value)s' is not a valid size unit. Allowed units are: %(allowed_units)s.")
    code = 'invalid_size_unit'

    def __init__(self, allowed_units=None):
        possible_units = ['rem', 'px', 'em', '%']
        if allowed_units is None:
            self.allowed_units = possible_units
        else:
            self.allowed_units = [au for au in allowed_units if au in possible_units]
        self.validation_pattern = re.compile(r'^(-?\d+)({})$'.format('|'.join(self.allowed_units)))

    def __call__(self, value):
        match = self.validation_pattern.match(value)
        if not (match and match.group(1).isdigit()):
            allowed_units = " {} ".format(ugettext("or")).join("'{}'".format(u) for u in self.allowed_units)
            params = {'value': value, 'allowed_units': allowed_units}
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.allowed_units == other.allowed_units and
            self.message == other.message and
            self.code == other.code
        )


class SizeField(Field):
    """
    Use this field for validating input containing a value ending in ``px``, ``em``, ``rem`` or ``%``.
    Use it for values representing a size, margin, padding, width or height.
    """
    def __init__(self, *, allowed_units=None, **kwargs):
        self.empty_value = ''
        super().__init__(**kwargs)
        self.validators.append(SizeUnitValidator(allowed_units))
        self.validators.append(ProhibitNullCharactersValidator())

    def to_python(self, value):
        """Return a stripped string."""
        if value not in self.empty_values:
            value = str(value).strip()
        if value in self.empty_values:
            return self.empty_value
        return value
