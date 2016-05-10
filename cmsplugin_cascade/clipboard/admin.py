# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.templatetags.admin_static import static
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.api import add_plugin
from cms.models.placeholdermodel import Placeholder
from cms.models.placeholderpluginmodel import PlaceholderReference
from cms.plugin_pool import plugin_pool
from cms.utils import get_language_from_request
from jsonfield.fields import JSONField
from djangocms_text_ckeditor.models import Text
from cmsplugin_cascade.models import CascadeClipboard


class JSONAdminWidget(widgets.Textarea):
    def __init__(self):
        attrs = {'cols': '40', 'rows': '3'}
        super(JSONAdminWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        id_data = attrs.get('id', 'id_data')
        clippy_url = static('cascade/admin/clippy.svg')
        return format_html('<textarea{0}>\r\n{1}</textarea> '
            '<button data-clipboard-target="#{2}" type="button" title="{4}" class="clip-btn">'
                '<img src="{3}" alt="{4}">'
            '</button>\n'
            '<div class="status-line"><label></label><strong id="pasted_success">{5}</strong>'
            '<strong id="copied_success">{6}</strong></div>',
            flatatt(final_attrs), force_text(value), id_data, clippy_url,
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
                           _("Save"))
    save_clipboard.short_description = _("From CMS Clipboard")

    def restore_clipboard(self, obj):
        return format_html('<input type="submit" value="{}" class="default pull-left" name="restore_clipboard" />',
                           _("Restore"))
    restore_clipboard.short_description = _("To CMS Clipboard")

    def save_model(self, request, obj, form, change):
        language = get_language_from_request(request)
        if request.POST.get('save_clipboard'):
            obj.data = self._serialize_clipboard(language)
            request.POST['_continue'] = True
        if request.POST.get('restore_clipboard'):
            request.POST['_continue'] = True
        super(CascadeClipboardAdmin, self).save_model(request, obj, form, change)
        if request.POST.get('restore_clipboard'):
            self._deserialize_clipboard(language, obj.data)

    def _serialize_clipboard(self, language):
        """
        Create a serialized representation of all the plugins belonging to the clipboard.
        """
        def populate_data(parent, data):
            for child in plugin_qs.filter(parent=parent):
                instance, dummy = child.get_plugin_instance(self.admin_site)
                try:
                    entry = (child.plugin_type, instance.get_data_representation(), [])
                except AttributeError:
                    if isinstance(instance, Text):
                        entry = (child.plugin_type, {'body': instance.body}, [])
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

    def _deserialize_clipboard(self, language, data):
        """
        Restore clipboard by creating plugins from given data.
        """
        def plugins_from_data(parent, data):
            for entry in data:
                plugin_type = plugin_pool.get_plugin(entry[0])
                kwargs = dict(entry[1])
                instance = add_plugin(clipboard, plugin_type, language, target=parent, **kwargs)
                # for some unknown reasons add_plugin sets instance.numchild 0,
                # but fixing and save()-ing 'instance' executes some filters in an unwanted manner
                plugins_from_data(instance, entry[2])

        clipboard = Placeholder.objects.filter(slot='clipboard').last()
        clipboard.cmsplugin_set.all().delete()
        plugins_from_data(None, data['plugins'])
