from django.forms import widgets, CharField, ModelChoiceField, Select
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from cmsplugin_cascade.models import CascadeElement, IconFont

from formset.forms import ModelForm


class IconFontChoiceField(ModelChoiceField):
    def __init__(self, **kwargs):
        kwargs.setdefault('queryset', IconFont.objects.all())
        kwargs.setdefault('empty_label', _("No Icon"))
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
            self.declared_fields['icon_font'].initial = None
            self.declared_fields['glyph'].required = False
        super().__init__(*args, **kwargs)

    def get_initial_for_field(self, field, field_name):
        if field == 'icon_font':
            try:
                return IconFont.objects.get(is_default=True)
            except IconFont.DoesNotExist:
                pass
        return super().get_initial_for_field(field, field_name)


def extract_stylesheet_urls(content):
    """
    Extract stylesheet URLs for icon fonts used in the content created by the RichtextArea widget.
    """

    stylesheet_urls = []
    for node in content:
        if node.get('type') == 'glyph':
            try:
                icon_font = IconFont.objects.get(id=node['attrs']['dataset']['font_id'])
            except (IconFont.DoesNotExist, KeyError):
                continue
            stylesheet_urls.append(icon_font.get_stylesheet_url())
        elif 'content' in node:
            stylesheet_urls.extend(extract_stylesheet_urls(node['content']))
    return stylesheet_urls
