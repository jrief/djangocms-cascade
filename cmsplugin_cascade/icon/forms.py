from django.forms import widgets, CharField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.icon.cms_plugins import get_default_icon_font
from cmsplugin_cascade.models import IconFont
from entangled.forms import EntangledModelFormMixin


class IconFontForm(EntangledModelFormMixin):
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
