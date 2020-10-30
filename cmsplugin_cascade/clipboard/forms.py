from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from cms.models import Placeholder
from cmsplugin_cascade.models import CascadeClipboard


class ClipboardBaseForm(forms.Form):
    placeholder = forms.ModelChoiceField(
        queryset=Placeholder.objects.all(),
        required=True,
        widget=forms.HiddenInput(),
    )

    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        required=True,
        widget=forms.HiddenInput(),
    )

    def clean_identifier(self):
        identifier = self.cleaned_data['identifier']
        if CascadeClipboard.objects.filter(identifier=identifier).exists():
            msg = _("This identifier has already been used, please choose another one.")
            raise ValidationError(msg)
        return identifier
