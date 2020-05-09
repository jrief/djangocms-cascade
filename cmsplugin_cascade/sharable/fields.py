from django.core.exceptions import ValidationError
from django.forms import widgets
from django.forms.fields import CharField, BooleanField, MultiValueField
from django.utils.translation import gettext_lazy as _


class SharedSettingsWidget(widgets.MultiWidget):
    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/sharedsettingsfield.js']

    def __init__(self):
        widget_list = [
            widgets.CheckboxInput(),
            widgets.TextInput(),
        ]
        super().__init__(widget_list)

    def decompress(self, value):
        return value


class SharedSettingsField(MultiValueField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('required', None)
        fields = [
            BooleanField(required=False),
            CharField(required=False),
        ]
        widget = kwargs.pop('widget', SharedSettingsWidget)
        initial = [False, '']
        super().__init__(fields=fields, widget=widget, initial=initial, required=False, *args, **kwargs)

    def clean(self, value):
        if value[0] and not value[1]:
            msg = _("An identifier is required to remember these settings.")
            raise ValidationError(msg)
        return value[1]
