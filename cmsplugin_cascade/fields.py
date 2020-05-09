import re
import json
import warnings

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ManyToOneRel
from django.forms import widgets
from django.forms.fields import Field, CharField, ChoiceField, BooleanField, MultiValueField
from django.forms.utils import ErrorList
from django.core.validators import ProhibitNullCharactersValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _, pgettext
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.widgets import ColorPickerWidget, BorderChoiceWidget, MultipleTextInputWidget
from filer.fields.image import FilerImageField, AdminImageFormField
from filer.settings import settings as filer_settings


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
        with_alpha = kwargs.pop('with_alpha', app_settings.CMSPLUGIN_CASCADE['color_picker_with_alpha'])
        widget = kwargs.pop('widget', BorderChoiceWidget(choices, with_alpha))
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

    @classmethod
    def css_value(self, values):
        return ' '.join(values)


class SelectTextAlignField(ChoiceField):
    CHOICES = [('left', 'left'), ('center', 'center'), ('right', 'right'), ('justify', 'justify')]

    def __init__(self, *args, **kwargs):
        super().__init__(choices=self.CHOICES, *args, **kwargs)


class SelectOverflowField(ChoiceField):
    CHOICES = [('auto', 'auto'), ('scroll', 'scroll'), ('hidden', 'hidden')]

    def __init__(self, *args, **kwargs):
        super().__init__(choices=self.CHOICES, *args, **kwargs)


@deconstructible
class ColorValidator():
    message = _("'%(color)s' is not a valid color code. ")
    code = 'invalid_color_code'

    def __init__(self, with_alpha):
        if with_alpha:
            self.validation_pattern = re.compile(r'(#(?:[0-9a-fA-F]{2}){2,4}|(#[0-9a-fA-F]{3})|(rgb|hsl)a?\((-?\d+%?[,\s]+){2,3}\s*[\d\.]+%?\))')
        else:
            self.validation_pattern = re.compile(r'(#(?:[0-9a-fA-F]{2}){2,3}|(#[0-9a-fA-F]{3})|(rgb|hsl))')

    def __call__(self, value):
        color, inherit = value
        match = self.validation_pattern.match(color)
        if not (inherit or match):
            params = {'color': color}
            raise ValidationError(self.message, code=self.code, params=params)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.validation_pattern == other.validation_pattern and
            self.message == other.message and
            self.code == other.code
        )


class ColorField(MultiValueField):
    DEFAULT_COLOR = '#808080'

    def __init__(self, inherit_color=False, default_color=DEFAULT_COLOR, *args, **kwargs):
        kwargs.pop('required', None)
        with_alpha = kwargs.pop('with_alpha', app_settings.CMSPLUGIN_CASCADE['color_picker_with_alpha'])
        widget = kwargs.pop('widget', ColorPickerWidget(with_alpha))
        fields = [
            CharField(initial=default_color),
            BooleanField(initial=inherit_color, required=False),
        ]
        kwargs['initial'] = [default_color, inherit_color]
        super().__init__(fields=fields, widget=widget, *args, **kwargs)
        self.validators.append(ColorValidator(with_alpha))
        self.validators.append(ProhibitNullCharactersValidator())

    def compress(self, data_list):
        self.run_validators(data_list)
        return data_list

    @classmethod
    def css_value(self, values):
        return values[0]


@deconstructible
class SizeUnitValidator():
    allowed_units = []
    message = _("'%(value)s' is not a valid size unit. Allowed units are: %(allowed_units)s.")
    code = 'invalid_size_unit'

    def __init__(self, allowed_units=None, allow_negative=True):
        possible_units = ['rem', 'px', 'em', '%', 'auto']
        if allowed_units is None:
            self.allowed_units = possible_units
        else:
            self.allowed_units = [au for au in allowed_units if au in possible_units]
        units_with_value = list(self.allowed_units)
        if 'auto' in self.allowed_units:
            self.allow_auto = True
            units_with_value.remove('auto')
        else:
            self.allow_auto = False
        if allow_negative:
            patterns = r'^(-?\d+(\.\d+)?)({})$'.format('|'.join(units_with_value))
        else:
            patterns = r'^(\d+(\.\d+)?)({})$'.format('|'.join(units_with_value))
        self.validation_pattern = re.compile(patterns)

    def __call__(self, value):
        if self.allow_auto and value == 'auto':
            return
        match = self.validation_pattern.match(value)
        try:
            float(match.group(1))
        except (AttributeError, ValueError):
            allowed_units = " {} ".format(pgettext('allowed_units', "or")).join("'{}'".format(u) for u in self.allowed_units)
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


class MultiSizeField(MultiValueField):
    """
    Some size input fields must be specified per Bootstrap breakpoint. Use this multiple
    input field to handle this.
    """
    def __init__(self, properties, *args, **kwargs):
        required = kwargs.pop('required', False)
        require_all_fields = kwargs.pop('require_all_fields', required)
        initial = kwargs.pop('initial', None)
        if isinstance(initial, (list, tuple)):
            if len(initial) != len(properties):
                raise ValueError("The number of initial values must be {}.".format(len(properties)))
            initial = dict(zip(properties, initial))
        elif not isinstance(initial, dict):
            initial = {prop: initial for prop in properties}
        allowed_units = kwargs.pop('allowed_units', None)
        fields = [SizeField(required=required, allowed_units=allowed_units)] * len(properties)
        widget = MultipleTextInputWidget(properties)
        super().__init__(fields=fields, widget=widget, required=required,
                         require_all_fields=require_all_fields, initial=initial, *args, **kwargs)
        self.properties = list(properties)

    def prepare_value(self, value):
        """Transform dict from DB into list"""
        if isinstance(value, dict):
            return [value.get(prop) for prop in self.properties]
        return value

    def compress(self, data_list):
        """Transform list into dict for DB"""
        return {prop: value for prop, value in zip(self.properties, data_list)}


class HiddenDictField(Field):
    widget = widgets.HiddenInput

    def prepare_value(self, value):
        """Transform dict from DB into list"""
        if isinstance(value, dict):
            return json.dumps(value)
        return value

    def clean(self, value):
        try:
            return json.loads(value)
        except:
            raise ValidationError("Invalid Field Value")


class CascadeImageField(AdminImageFormField):
    def __init__(self, *args, **kwargs):
        model_name_tuple = filer_settings.FILER_IMAGE_MODEL.split('.')
        Image = apps.get_model(*model_name_tuple, require_ready=False)
        kwargs.setdefault('label', _("Image"))
        super().__init__(
            ManyToOneRel(FilerImageField, Image, 'file_ptr'),
            Image.objects.all(),
            'image_file', *args, **kwargs)
