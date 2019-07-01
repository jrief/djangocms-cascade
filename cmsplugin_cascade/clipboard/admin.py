from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.templatetags.admin_static import static
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from cms.api import add_plugin
from cms.models.placeholderpluginmodel import PlaceholderReference
from cms.plugin_pool import plugin_pool
from cms.utils import get_language_from_request

from jsonfield.fields import JSONField
from djangocms_text_ckeditor.models import Text
from djangocms_text_ckeditor.utils import plugin_tags_to_id_list, replace_plugin_tags

from cmsplugin_cascade.models import CascadeElement, CascadeClipboard
from cmsplugin_cascade.clipboard.library.utils import deserialize_to_clipboard

class JSONAdminWidget(widgets.Textarea):
    def __init__(self):
        attrs = {'cols': '40', 'rows': '3'}
        super(JSONAdminWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(self.attrs, extra_attrs=dict(attrs, name=name))
        id_data = attrs.get('id', 'id_data')
        clippy_url = static('cascade/admin/clippy.svg')
        return format_html('<textarea{0}>\r\n{1}</textarea> '
            '<button data-clipboard-target="#{2}" type="button" title="{4}" class="clip-btn">'
                '<img src="{3}" alt="{4}">'
            '</button>\n'
            '<div class="status-line"><label></label><strong id="pasted_success">{5}</strong>'
            '<strong id="copied_success">{6}</strong></div>',
            flatatt(final_attrs), str(value), id_data, clippy_url,
            _("Copy to Clipboard"),
            _("Successfully pasted JSON data"),
            _("Successfully copied JSON data"))


@admin.register(CascadeClipboard)
class CascadeClipboardAdmin(admin.ModelAdmin):
    fields = ('identifier', 'save_clipboard', 'restore_clipboard', 'data',)
    readonly_fields = ('save_clipboard', 'restore_clipboard',)
    formfield_overrides = {
        JSONField: {'widget': JSONAdminWidget},
    }

    class Media:
        css = {'all': ('cascade/css/admin/clipboard.css',)}
        js = ('cascade/js/admin/clipboard.js',)

    def save_clipboard(self, obj):
        return format_html('<input type="submit" value="{}" class="default pull-left" name="save_clipboard" />',
                           _("Insert Data"))
    save_clipboard.short_description = _("From CMS Clipboard")

    def restore_clipboard(self, obj):
        return format_html('<input type="submit" value="{}" class="default pull-left" name="restore_clipboard" />',
                           _("Restore Data"))
    restore_clipboard.short_description = _("To CMS Clipboard")

    def save_model(self, request, obj, form, change):
        language = get_language_from_request(request)
        if request.POST.get('save_clipboard'):
            obj.data = self._serialize_from_clipboard(language)
            request.POST = request.POST.copy()
            request.POST['_continue'] = True
            messages.add_message(request, messages.INFO, _("The CMS clipboard has been persisted in the database."))
        if request.POST.get('restore_clipboard'):
            request.POST = request.POST.copy()
            request.POST['_continue'] = True
            messages.add_message(request, messages.INFO, _("Persisted content has been restored to CMS clipboard."))
        super().save_model(request, obj, form, change)
        if request.POST.get('restore_clipboard'):
            deserialize_to_clipboard(request, obj.data)


    def _serialize_from_clipboard(self, language):
        """
        Create a serialized representation of all the plugins belonging to the clipboard.
        """
        def populate_data(parent, data):
            for child in plugin_qs.filter(parent=parent).order_by('position'):
                instance, plugin = child.get_plugin_instance(self.admin_site)
                plugin_type = plugin.__class__.__name__
                try:
                    entry = (plugin_type, plugin.get_data_representation(instance), [])
                except AttributeError:
                    if isinstance(instance, Text):
                        entry = (plugin_type, {'body': instance.body, 'pk': instance.pk}, [])
                    else:
                        continue
                data.append(entry)
                populate_data(child, entry[2])

        data = {'plugins': []}
        ref = PlaceholderReference.objects.last()
        if ref:
            clipboard = ref.placeholder_ref
            plugin_qs = clipboard.cmsplugin_set.all()
            populate_data(None, data['plugins'])
        return data
