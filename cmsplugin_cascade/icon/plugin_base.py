from django.utils.safestring import mark_safe
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase
from entangled.forms import get_related_object


class IconPluginMixin(CascadePluginMixinBase):
    change_form_template = 'cascade/admin/change_form.html'
    ring_plugin = 'IconPluginMixin'

    class Media:
        css = {'all': ['cascade/css/admin/iconplugin.css']}
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/iconpluginmixin.js']

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super().changeform_view(request, object_id, form_url, extra_context)

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        icon_font = get_related_object(instance.glossary, 'icon_font')
        symbol = instance.glossary.get('symbol')
        if icon_font and symbol:
            prefix = icon_font.config_data.get('css_prefix_text', 'icon-')
            context.update({
                'stylesheet_url': icon_font.get_stylesheet_url(),
                'icon_font_class': mark_safe('{}{}'.format(prefix, symbol)),
            })
        return context
