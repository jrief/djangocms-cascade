# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION
from django.contrib import admin
from django.contrib.admin.templatetags.admin_static import static
from django.forms import widgets
from django.forms.utils import flatatt
from django.http import HttpResponse
from django.contrib import messages
from django.utils.encoding import force_text
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

from .utils import (add_size_img_to_json, gen_img_if_pk_and_size_not_match)

class JSONAdminWidget(widgets.Textarea):
    def __init__(self):
        attrs = {'cols': '40', 'rows': '3'}
        super(JSONAdminWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        if DJANGO_VERSION < (1, 11):
            final_attrs = self.build_attrs(attrs, name=name)
        else:
            final_attrs = self.build_attrs(self.attrs, extra_attrs=dict(attrs, name=name))
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

    def get_changeform_initial_data(self, request):
        return {'identifier': "Clipboard {}".format(CascadeClipboard.objects.all().count()+1)}

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
            obj.data = self._serialize_from_clipboard(request, language)
            request.POST = request.POST.copy()
            request.POST['_continue'] = True
        if request.POST.get('restore_clipboard'):
            request.POST = request.POST.copy()
            request.POST['_continue'] = True
        super(CascadeClipboardAdmin, self).save_model(request, obj, form, change)
        is_placeholder=None
        if 'plugins' in obj.data:
            if len(obj.data['plugins']) >= 2:
                is_placeholder=True
        self._deserialize_to_clipboard(request, obj.data, is_placeholder)

    def _serialize_from_clipboard(self, request, language, clipboard=None):
        """
        Create a serialized representation of all the plugins belonging to the clipboard.
        """
        def populate_data(parent, data):
            for child in plugin_qs.filter(parent=parent).order_by('position'):
                instance, plugin = child.get_plugin_instance(self.admin_site)
                plugin_type = plugin.__class__.__name__
                try:
                    entry = (plugin_type, plugin.get_data_representation(instance), [])
                    add_size_img_to_json(instance,plugin)
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
        elif request.toolbar.clipboard.cmsplugin_set.last():
            clipboard = request.toolbar.clipboard
        if clipboard is not None:
            plugin_qs = clipboard.cmsplugin_set.all()
            populate_data(None, data['plugins'])
        return data

    def _deserialize_to_clipboard(self, request, data, is_placeholder):
        """
        Restore clipboard by creating plugins from given data.
        """
        def plugins_from_data(placeholder, parent, data):
            for plugin_type, data, children_data in data:
                plugin_class = plugin_pool.get_plugin(plugin_type)
                gen_img_if_pk_and_size_not_match(data)
                kwargs = dict(data)
                inlines = kwargs.pop('inlines', [])
                shared_glossary = kwargs.pop('shared_glossary', None)
                instance = add_plugin(placeholder, plugin_class, language, target=parent, **kwargs)
                if isinstance(instance, CascadeElement):
                    instance.plugin_class.add_inline_elements(instance, inlines)
                    instance.plugin_class.add_shared_reference(instance, shared_glossary)
                if not 'plugins' in data:
                    data = {'plugins': []}

                # for some unknown reasons add_plugin sets instance.numchild to 0,
                # but fixing and save()-ing 'instance' executes some filters in an unwanted manner
                plugins_from_data(placeholder, instance, children_data)

                if isinstance(instance, Text):
                    # we must convert the old plugin IDs into the new ones,
                    # otherwise links are not displayed
                    id_dict = dict(zip(
                        plugin_tags_to_id_list(instance.body),
                        (t[0] for t in instance.get_children().values_list('id'))
                    ))
                    instance.body = replace_plugin_tags(instance.body, id_dict)
                    instance.save()

        language = get_language_from_request(request)

        clipboard = request.toolbar.clipboard
        ref_plugin = clipboard.cmsplugin_set.first()
        if ref_plugin is None and is_placeholder is True:
            # the clipboard is empty
            root_plugin = add_plugin(clipboard, 'PlaceholderPlugin', language, name='clipboard')
            root_plugin=root_plugin.placeholder_ref
        elif is_placeholder is True:
            # remove old entries from the clipboard
            root_plugin = ref_plugin.cms_placeholderreference
            inst = ref_plugin.get_plugin_instance()[0]
            inst.placeholder_ref.get_plugins().delete()
            root_plugin=root_plugin.placeholder_ref
        elif is_placeholder is None:
            root_plugin=clipboard
            if ref_plugin:
                inst = ref_plugin.get_plugin_instance()[0]
                inst.placeholder.get_plugins().delete()
        plugins_from_data(root_plugin, None, data['plugins'])

    def response_change(self, request, obj):
        #Little hack to reload the clipboard modified in Django administration and the sideframe Django-CMS.
        #TODO find a better way to reload clipboard potentially with request Ajax
        #js = static_with_version('cms/js/dist/bundle.admin.base.min.js')
        if "restore_clipboard" in request.POST:
            return HttpResponse(
            format_html('<script type="text/javascript">window.parent.CMS.API.Helpers.reloadBrowser();</script>'))
        return super().response_change(request, obj)

