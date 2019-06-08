from django.forms.models import ModelChoiceField
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase
from entangled.forms import get_related_object


class IconPluginMixin(CascadePluginMixinBase):
    change_form_template = 'cascade/admin/fonticon_change_form.html'
    ring_plugin = 'IconPluginMixin'
    require_icon_font = True  # if False, the icon_font is optional

    class Media:
        css = {'all': ['cascade/css/admin/iconplugin.css']}
        js = ['cascade/js/admin/iconpluginmixin.js']

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(IconPluginMixin, cls).get_identifier(instance)
        icon_font = cls.get_icon_font(instance)
        symbol = instance.glossary.get('symbol')
        if icon_font and symbol:
            prefix = icon_font.config_data['css_prefix_text']
            return format_html('{0}{1}{2}', identifier, prefix, symbol)
        return identifier

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super(IconPluginMixin, self).changeform_view(
             request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, **kwargs):
        icon_font_field = [gf for gf in self.glossary_fields if gf.name == 'icon_font'][0]
        icon_font_field.widget.choices = IconFont.objects.values_list('id', 'identifier')
        form = super(IconPluginMixin, self).get_form(request, obj=obj, **kwargs)
        return form

    @classmethod
    def get_icon_font(self, instance):
        if not hasattr(instance, '_cached_icon_font'):
            try:
                instance._cached_icon_font = IconFont.objects.get(id=instance.glossary['icon_font'])
            except (IconFont.DoesNotExist, KeyError, ValueError):
                instance._cached_icon_font = None
        return instance._cached_icon_font

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        icon_font = self.get_icon_font(instance)
        if icon_font:
            context['stylesheet_url'] = icon_font.get_stylesheet_url()
        return context


class IconPluginMixin2(CascadePluginMixinBase):
    change_form_template = 'cascade/admin/fonticon_change_form.html'
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
        if 'form' in kwargs:
            kwargs['form'] = type(kwargs['form'].__name__, (IconFontFormMixin, kwargs['form']), attrs)
        else:
            kwargs['form'] = type('IconFontForm', (IconFontFormMixin,), attrs)
        return super().get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        context = self.super(IconPluginMixin2, self).render(context, instance, placeholder)
        icon_font = get_related_object(instance.glossary, 'icon_font')
        symbol = instance.glossary.get('symbol')
        if icon_font and symbol:
            prefix = icon_font.config_data.get('css_prefix_text', 'icon-')
            context.update({
                'stylesheet_url': icon_font.get_stylesheet_url(),
                'icon_font_class': mark_safe('{}{}'.format(prefix, symbol)),
            })
        return context
