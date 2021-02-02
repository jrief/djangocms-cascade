from django.contrib import admin
from django.contrib import messages
from django.forms import widgets
from django.forms.utils import flatatt
from django.db.models import JSONField
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from cms.models.placeholderpluginmodel import PlaceholderReference
from cmsplugin_cascade.clipboard.utils import deserialize_to_clipboard, serialize_from_placeholder
from cmsplugin_cascade.models import CascadeClipboard


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
    fields = ['identifier', ('created_by', 'created_at', 'last_accessed_at'), 'save_clipboard', 'restore_clipboard', 'data']
    readonly_fields = ['created_by', 'created_at', 'last_accessed_at', 'save_clipboard', 'restore_clipboard']
    formfield_overrides = {
        JSONField: {'widget': JSONAdminWidget},
    }
    list_display = ['identifier', 'created_by', 'created_at']

    class Media:
        css = {'all': ['cascade/css/admin/clipboard.css']}
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/clipboard.js']

    def save_clipboard(self, obj):
        return format_html('<input type="submit" value="{}" class="default pull-left" name="save_clipboard" />',
                           _("Insert Data"))
    save_clipboard.short_description = _("From CMS Clipboard")

    def restore_clipboard(self, obj):
        return format_html('<input type="submit" value="{}" class="default pull-left" name="restore_clipboard" />',
                           _("Restore Data"))
    restore_clipboard.short_description = _("To CMS Clipboard")

    def save_model(self, request, obj, form, change):
        if request.POST.get('save_clipboard'):
            placeholder_reference = PlaceholderReference.objects.last()
            if placeholder_reference:
                placeholder = placeholder_reference.placeholder_ref
                obj.data = serialize_from_placeholder(placeholder, self.admin_site)
            request.POST = request.POST.copy()
            request.POST['_continue'] = True
            messages.add_message(request, messages.INFO, _("The CMS clipboard has been persisted into the database."))
        if request.POST.get('restore_clipboard'):
            request.POST = request.POST.copy()
            request.POST['_continue'] = True
            messages.add_message(request, messages.INFO, _("Persisted content has been restored to CMS clipboard."))
        if request.POST.get('restore_clipboard'):
            deserialize_to_clipboard(request, obj.data)
            obj.last_accessed_at = now()
        super().save_model(request, obj, form, change)

