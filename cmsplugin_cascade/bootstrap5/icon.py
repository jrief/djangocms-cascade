from django.forms import widgets, CharField, ModelChoiceField
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.models import CascadeElement

from formset.forms import ModelForm


class IconFontChoiceField(ModelChoiceField):
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', IconFont.objects.all())
        kwargs.setdefault('empty_label', _("No Icon"))
        try:
            initial = IconFont.objects.get(is_default=True).id
        except IconFont.DoesNotExist:
            initial = ''
        kwargs.setdefault('initial', initial)
        super().__init__(**kwargs)


class GlyphIconForm(ModelForm):
    icon_font = IconFontChoiceField(
        label=_("Icon-Font"),
    )
    glyph = CharField(
        label=_("Glyph"),
        widget=widgets.TextInput(attrs={
            'is': 'cascade-select-glyph',
            'fonticon-field': 'icon_font',
            'fonticon-endpoint': reverse_lazy('admin:fetch_fonticons'),
        }),
        help_text=_("Select specific glyph from list of the selected icon font."),
    )

    class Meta:
        model = CascadeElement
        fields_map = {'glossary': ['icon_font', 'glyph']}

    def __init__(self, *args, **kwargs):
        if not getattr(self, 'require_icon', True):
            self.declared_fields['icon_font'].required = False
            self.declared_fields['icon_font'].empty_label = _("No Icon")
            self.declared_fields['icon_font'].initial = None
            self.declared_fields['glyph'].required = False
        super().__init__(*args, **kwargs)

    @property
    def media(self):
        media = super().media + widgets.Media(
            js=['cascade/admin/bootstrap5/js/formset-extensions.js'],
        )
        return media
