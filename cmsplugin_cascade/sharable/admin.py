from django.contrib import admin
from django.utils.translation import gettext as _
from django.utils.html import format_html
from entangled.forms import EntangledModelForm
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.plugin_base import CascadePluginMixinMetaclass
from cmsplugin_cascade.models import SharedGlossary, SharableCascadeElement


@admin.register(SharedGlossary)
class SharedGlossaryAdmin(admin.ModelAdmin):
    change_form_template = 'cascade/admin/sharedglossary_change_form.html'
    list_display = ['identifier', 'plugin_name', 'used_by']
    readonly_fields = ['plugin_name']
    list_filter = ['plugin_type']

    class Media:
        css = {'all': ['cascade/css/admin/partialfields.css', 'cascade/css/admin/editplugin.css']}

    def get_form(self, request, obj=None, **kwargs):
        """
        Creates a temporary form with an identifier and the fields declared as sharables for the
        corresponding plugin model. Additionally it adds dynamic fields to edit the content inside
        the model field `glossary`. The layout, validation and media files for these dynamic fields
        are borrowed from the corresponding plugin.
        """
        sharable_fields = getattr(self.plugin_instance, 'sharable_fields', [])
        form_mixin = self.plugin_instance().get_form(request)
        attrs = {name: field for name, field in form_mixin.base_fields.items() if name in sharable_fields}

        class Meta:
            untangled_fields = ['identifier']
            entangled_fields = {'glossary': list(attrs.keys())}

        attrs['Meta'] = Meta
        kwargs['form'] = type('SharedFieldsForm', (EntangledModelForm,), attrs)
        return super().get_form(request, obj, **kwargs)

    def has_add_permission(self, request):
        # always False, since a SharedGlossary can only be added by a plugin
        return False

    def add_view(self, request, form_url='', extra_context=None):
        raise AssertionError("This method shall never be called")

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        self.plugin_instance = plugin_pool.get_plugin(obj.plugin_type)
        extra_context = dict(extra_context or {},
                             title=format_html(_("Change shared settings of '{}' plugin"), self.plugin_instance.name),
                             icon_fonts=IconFont.objects.all())
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def used_by(self, obj):
        """
        Returns the number of plugins using this shared glossary
        """
        return SharableCascadeElement.objects.filter(shared_glossary=obj).count()
    used_by.short_description = _("Used by plugins")

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        try:
            context['media'] += self.plugin_instance().media
        except (AttributeError, KeyError):
            pass
        context.update(
            ring_plugin=self.plugin_instance().ring_plugin,
            ring_plugin_bases=dict((ring_plugin, ['django.cascade.{}'.format(b) for b in bases if b != 'SharableGlossaryMixin'])
                                   for ring_plugin, bases in CascadePluginMixinMetaclass.ring_plugin_bases.items())
        )
        return super().render_change_form(request, context, add, change, form_url, obj)

    def plugin_name(self, obj):
        plugin_instance = plugin_pool.get_plugin(obj.plugin_type)
        return plugin_instance.name
    plugin_name.short_description = _("Plugin Type")
