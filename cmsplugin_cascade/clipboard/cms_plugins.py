import json

from django.contrib.admin import site as default_admin_site
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.forms import CharField, ModelChoiceField
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import re_path, reverse
from django.utils.http import urlencode
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _, get_language_from_request

from cms.plugin_base import CMSPluginBase, PluginMenuItem
from cms.plugin_pool import plugin_pool
from cms.toolbar.utils import get_plugin_tree, get_toolbar_from_request
from cms.utils.plugins import copy_plugins_to_placeholder
from cmsplugin_cascade.clipboard.forms import ClipboardBaseForm
from cmsplugin_cascade.clipboard.utils import deserialize_to_clipboard, serialize_from_placeholder
from cmsplugin_cascade.models import CascadeClipboard, CascadeElement


class CascadeClipboardPlugin(CMSPluginBase):
    render_plugin = False
    change_form_template = 'admin/cms/page/plugin/change_form.html'

    def get_plugin_urls(self):
        urlpatterns = [
            re_path(r'^export-plugins/$', self.export_plugins_view, name='export_clipboard_plugins'),
            re_path(r'^import-plugins/$', self.import_plugins_view, name='import_clipboard_plugins'),
        ]
        return urlpatterns

    @classmethod
    def get_extra_placeholder_menu_items(cls, request, placeholder):
        data = urlencode({
            'placeholder': placeholder.pk,
            'language': get_language_from_request(request, check_path=True),
        })
        return [
            PluginMenuItem(
                _("Export to Clipboard"),
                reverse('admin:export_clipboard_plugins') + '?' + data,
                data={},
                action='modal',
                attributes={
                    'icon': 'export',
                },
            ),
            PluginMenuItem(
                _("Import from Clipboard"),
                reverse('admin:import_clipboard_plugins') + '?' + data,
                data={},
                action='modal',
                attributes={
                    'icon': 'import',
                },
            )
        ]

    def render_modal_window(self, request, form):
        """
        Render a modal popup window with a select box to edit the form
        """
        opts = self.model._meta
        fieldsets = [(None, {'fields': list(form.fields)})]
        adminForm = AdminForm(form, fieldsets, {}, [])
        context = {
            **default_admin_site.each_context(request),
            'title': form.title,
            'adminform': adminForm,
            'add': False,
            'change': True,
            'save_as': False,
            'has_add_permission': False,
            'has_change_permission': True,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'is_popup': True,
            'app_label': opts.app_label,
            'media': self.media + form.media,
        }
        return TemplateResponse(request, self.change_form_template, context)

    def import_plugins_view(self, request):
        # TODO: check for permissions

        title = _("Import from Clipboard")
        if request.method == 'GET':
            Form = type('ClipboardImportForm', (ClipboardBaseForm,), {
                'clipboard': ModelChoiceField(
                    queryset=CascadeClipboard.objects.all(),
                    label=_("Select Clipboard Content"),
                    required=False,
                ),
                'title': title,
            })
            form = Form(request.GET)
            assert form.is_valid()
        elif request.method == 'POST':
            Form = type('ClipboardImportForm', (ClipboardBaseForm,), {
                'clipboard': ModelChoiceField(
                    queryset=CascadeClipboard.objects.all(),
                    label=_("Select Clipboard Content"),
                ),
                'title': title,
            })
            form = Form(request.POST)
            if form.is_valid():
                return self.paste_from_clipboard(request, form)
        return self.render_modal_window(request, form)

    def paste_from_clipboard(self, request, form):
        target_placeholder = form.cleaned_data['placeholder']
        target_position = 1 # int(form.cleaned_data.get('target_position', '0'))  # 1
        language = form.cleaned_data['language']
        cascade_clipboard = form.cleaned_data['clipboard']
        deserialize_to_clipboard(request, cascade_clipboard.data)
        cascade_clipboard.last_accessed_at = now()
        cascade_clipboard.save(update_fields=['last_accessed_at'])

        # detach plugins from clipboard and reattach them to current placeholder
        clipboard = get_toolbar_from_request(request).clipboard
        cb_placeholder_plugin = clipboard.cmsplugin_set.filter(plugin_type='PlaceholderPlugin').first()
        cb_placeholder_instance, _ = cb_placeholder_plugin.get_plugin_instance()
        plugins = cb_placeholder_instance.placeholder_ref.get_plugins()
        tree_order = target_placeholder.get_plugin_tree_order(language, parent_id=cb_placeholder_plugin.id)
        new_plugins = copy_plugins_to_placeholder(
            plugins,
            placeholder=target_placeholder,
            language=language,
            start_positions={language: target_position},
        )
        new_plugin_ids = (new.pk for new in new_plugins)
        target_placeholder.clear_cache(language)
        new_plugins = list(
            CascadeElement
            .objects
            .filter(pk__in=new_plugin_ids)
            .select_related('placeholder')
        )

        data = get_plugin_tree(request, new_plugins)
        data['plugin_order'] = tree_order + ['__COPY__']
        data['target_placeholder_id'] = target_placeholder.pk
        context = {'structure_data': json.dumps(data)}
        return render(request, 'djangocms_transfer/placeholder_close_frame.html', context)

    def export_plugins_view(self, request):
        if not request.user.is_staff:
            raise PermissionDenied

        title = _("Export to Clipboard")
        if request.method == 'GET':
            Form = type('ClipboardExportForm', (ClipboardBaseForm,), {
                'identifier': CharField(required=False),
                'title': title,
            })
            form = Form(request.GET)
            assert form.is_valid()
        elif request.method == 'POST':
            Form = type('ClipboardExportForm', (ClipboardBaseForm,), {
                'identifier': CharField(),
                'title': title,
            })
            form = Form(request.POST)
            if form.is_valid():
                return self.add_to_clipboard(request, form)
        return self.render_modal_window(request, form)

    def add_to_clipboard(self, request, form):
        placeholder = form.cleaned_data['placeholder']
        language = form.cleaned_data['language']
        identifier = form.cleaned_data['identifier']
        data = serialize_from_placeholder(placeholder)
        CascadeClipboard.objects.create(
            identifier=identifier,
            data=data,
            created_by=request.user,
        )
        return render(request, 'cascade/admin/clipboard_close_frame.html', {})

plugin_pool.register_plugin(CascadeClipboardPlugin)
