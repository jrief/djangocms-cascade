import re
import warnings
from django.forms import widgets
from django.forms.fields import Field
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError
from django.core.validators import ProhibitNullCharactersValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _, ugettext


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


@deconstructible
class SizeUnitValidator():
    allowed_units = []
    message = _(
        "'%(value)s' is not a valid size unit. "
        "Allowed units are: %(allowed_units)s."
    )
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
