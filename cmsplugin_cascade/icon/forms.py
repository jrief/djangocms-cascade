from django.forms import widgets, CharField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.models import IconFont
from entangled.forms import EntangledModelFormMixin


def get_default_icon_font():
    try:
        return IconFont.objects.get(is_default=True).id
    except IconFont.DoesNotExist:
        return ''


class IconFontFormMixin(EntangledModelFormMixin):
    icon_font = ModelChoiceField(
        IconFont.objects.all(),
        label=_("Font"),
        initial=get_default_icon_font,
    )

    symbol = CharField(
        widget=widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    class Meta:
        entangled_fields = {'glossary': ['icon_font', 'symbol']}
