from django.forms.models import ModelChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from entangled.forms import EntangledModelFormMixin
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase
from entangled.forms import get_related_object


class IconPluginMixin(CascadePluginMixinBase):
    change_form_template = 'cascade/admin/change_form.html'
    ring_plugin = 'IconPluginMixin'
    require_icon_font = True  # if False, the icon_font is optional

    class Media:
        css = {'all': ['cascade/css/admin/iconplugin.css']}
        js = ['cascade/js/admin/iconpluginmixin.js']

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        from cmsplugin_cascade.icon.forms import IconFontFormMixin

        attrs = {}
        if not getattr(self, 'require_icon', True):
            # if the icon is optional, override choice field to reflect this
            attrs['icon_font'] = ModelChoiceField(
                IconFont.objects.all(),
                label=_("Font"),
                empty_label=_("No Icon"),
                required=False,
            )
        form = kwargs.get('form', self.form)
        assert issubclass(form, EntangledModelFormMixin), "Form must inherit from EntangledModelFormMixin"
        kwargs['form'] = type(form.__name__, (IconFontFormMixin, form), attrs)
        return super().get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        context = self.super(IconPluginMixin, self).render(context, instance, placeholder)
        icon_font = get_related_object(instance.glossary, 'icon_font')
        symbol = instance.glossary.get('symbol')
        if icon_font and symbol:
            prefix = icon_font.config_data.get('css_prefix_text', 'icon-')
            context.update({
                'stylesheet_url': icon_font.get_stylesheet_url(),
                'icon_font_class': mark_safe('{}{}'.format(prefix, symbol)),
            })
        return context
