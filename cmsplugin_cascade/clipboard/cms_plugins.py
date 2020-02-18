import json
from django.conf.urls import url
from django.contrib.admin import site as default_admin_site
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.forms import CharField, ModelChoiceField, ModelMultipleChoiceField
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase, PluginMenuItem
from cms.plugin_pool import plugin_pool
from cms.toolbar.utils import get_plugin_tree_as_json
from cms.utils import get_language_from_request
from cmsplugin_cascade.clipboard.forms import ClipboardBaseForm
from cmsplugin_cascade.clipboard.utils import deserialize_to_clipboard, serialize_from_placeholder
from cmsplugin_cascade.models import CascadeClipboard, CascadeClipboardGroup
from cmsplugin_cascade.clipboard.forms import ClipboardBaseForm
from django.forms import widgets
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

class ClipboardWidget(widgets.Select):
        template_name = 'django/forms/widgets/select.html'
        #template_name = 'cascade/admin/widgets/clipboard.html'


class CascadeClipboardPlugin(CMSPluginBase):
    system = True
    render_plugin = False
    change_form_template = 'admin/cms/page/plugin/change_form.html'

    def get_plugin_urls(self):
        urlpatterns = [
            url(r'^export-plugins/$', self.export_plugins_view, name='export_clipboard_plugins'),
            url(r'^import-plugins/$', self.import_plugins_view, name='import_clipboard_plugins'),
        ]
        return urlpatterns

    @classmethod
    def get_extra_placeholder_menu_items(cls, request, placeholder):
        data = urlencode({
            'placeholder': placeholder.pk,
            'language': get_language_from_request(request),
        })
        return [
            PluginMenuItem(
                _("Export from Clipboard"),
                reverse('admin:export_clipboard_plugins') + '?' + data,
                data={},
                action='modal',
                attributes={
                    'icon': 'import',
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
            ),
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
            'add': True,
            'change': True,
            'save_as': True,
            'has_add_permission': True,
            'has_change_permission': True,
            'can_change_related':True,
            'can_add_related':True,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'is_popup': True,
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
                    widget=ClipboardWidget,
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
                    widget=ClipboardWidget,
                ),
                'title': title,
            })
            form = Form(request.POST)
            if form.is_valid():
                return self.paste_from_clipboard(request, form)
        return self.render_modal_window(request, form)

    def paste_from_clipboard(self, request, form):
        placeholder = form.cleaned_data['placeholder']
        language = form.cleaned_data['language']
        cascade_clipboard = form.cleaned_data['clipboard']
        tree_order = placeholder.get_plugin_tree_order(language)
        deserialize_to_clipboard(request, cascade_clipboard.data)

        # detach plugins from clipboard and reattach them to current placeholder
        cb_placeholder_plugin = request.toolbar.clipboard.cmsplugin_set.first()
        cb_placeholder_instance, _ = cb_placeholder_plugin.get_plugin_instance()
        new_plugins = cb_placeholder_instance.placeholder_ref.get_plugins()
        new_plugins.update(placeholder=placeholder)

        # reorder root plugins in placeholder
        root_plugins = placeholder.get_plugins(language).filter(parent__isnull=True).order_by('changed_date')
        for position, plugin in enumerate(root_plugins.iterator()):
            plugin.update(position=position)
        placeholder.mark_as_dirty(language, clear_cache=False)

        # create a list of pasted plugins to be added to the structure view
        all_plugins = placeholder.get_plugins(language)
        if all_plugins.exists():
            new_plugins = placeholder.get_plugins(language).exclude(pk__in=tree_order)
            data = json.loads(get_plugin_tree_as_json(request, list(new_plugins)))
            data['plugin_order'] = tree_order + ['__COPY__']
        else:
            return render(request, 'cascade/admin/clipboard_reload_page.html')
        data['target_placeholder_id'] = placeholder.pk
        context = {'structure_data': json.dumps(data)}
        return render(request, 'cascade/admin/clipboard_paste_plugins.html', context)

    def export_plugins_view(self, request):
        if not request.user.is_staff:
            raise PermissionDenied

        title = _("Export to Clipboard")
        if request.method == 'GET':
            Form = type('ClipboardExportForm', (ClipboardBaseForm,), {
                'identifier': CharField(required=False),
                'title': title,
                'group' : ModelMultipleChoiceField(
                queryset=CascadeClipboardGroup.objects.all(),
                required=False,
            ),
            })
            form = Form(request.GET)
            form.fields['group'].widget = RelatedFieldWidgetWrapper(
              form.fields['group'].widget,CascadeClipboard.group.rel,
                default_admin_site, can_change_related=True)

            assert form.is_valid()
        elif request.method == 'POST':
            Form = type('ClipboardExportForm', (ClipboardBaseForm,), {
                'identifier': CharField(),
                'title': title,
                'group' : ModelMultipleChoiceField(
                queryset=CascadeClipboardGroup.objects.all(),
                required=False,
            ),
            })
            form = Form(request.POST)
            form.fields['group'].widget = RelatedFieldWidgetWrapper(
              form.fields['group'].widget,CascadeClipboard.group.rel,
                default_admin_site, can_change_related=True) 

            if form.is_valid():
                return self.add_to_clipboard(request, form)
        return self.render_modal_window(request, form)

    def add_to_clipboard(self, request, form):
        placeholder = form.cleaned_data['placeholder']
        language = form.cleaned_data['language']
        identifier = form.cleaned_data['identifier']
        group = form.cleaned_data['group']
        data = serialize_from_placeholder(placeholder)
        cascade_clipboard = CascadeClipboard.objects.create(
            identifier=identifier,
            data=data,
        )
        cascade_clipboard.group.set(group) 
        return render(request, 'cascade/admin/clipboard_close_frame.html', {})

plugin_pool.register_plugin(CascadeClipboardPlugin)
