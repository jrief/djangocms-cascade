import json
from django.conf.urls import url
from django.contrib.admin import site as default_admin_site
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.forms import CharField, ModelChoiceField, ModelMultipleChoiceField, ChoiceField, MultipleChoiceField
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
    #template_name = 'django/forms/widgets/select.html'
    template_name = 'cascade/admin/widgets/clipboard.html'

    def get_context(self, name, value, attrs):
        context = super(ClipboardWidget, self).get_context(name, value, attrs)
        context['widget']['optgroups'] = self.optgroups(name, context['widget']['value'], attrs)
        groups=list(CascadeClipboardGroup.objects.all().exclude( name='Clipboard Home').values_list('name',flat=True))
        context['groups_exclude_home'] = groups
        context['qs_clipboards'] = CascadeClipboard.objects.all()
        return context


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
            'app_label': opts.app_label,
            'media': self.media + form.media,
        }

        return TemplateResponse(request, self.change_form_template, context)


    def import_plugins_view(self, request, *args, **kwargs):
        # TODO: check for permissions

        placeholder_ref_id = None
        if request.GET.get('placeholder'):
            placeholder_ref_id = request.GET.get('placeholder')
        queryset=CascadeClipboard.objects.all().prefetch_related('group')
        clipboards_groupby={}

        def treegroup( groups, index2):
           groups_clipboard=list(groups.group.values_list('name', flat=True))
           if len(groups_clipboard) >= 1:
               for index, key in enumerate(groups_clipboard, start=1):
                   clipboards_groupby.setdefault(key, [])
                   clipboards_groupby[key].append(( groups.identifier ,groups.identifier,))
           else:
               clipboards_groupby.setdefault('ungroup', [])
               clipboards_groupby['ungroup'].append(( groups.identifier ,groups.identifier,))

        [treegroup( groups, index)  for index, groups in enumerate(queryset , start=1)]

        if not 'Clipboard Home' in clipboards_groupby:
            clipboards_groupby[ 'Clipboard Home'] = [('demo', 'demo')]
            clipboard_home = CascadeClipboardGroup.objects.create(name="Clipboard Home")
            data_demo = self.populate_static_json("demo_carousel-plugin.json")
            print(data_demo)
            group_clipboard_home = clipboard_home
            cascade_clipboard = CascadeClipboard.objects.create(
                identifier="demo",
                data=data_demo,
            )
            cascade_clipboard.group.set([group_clipboard_home])

        CHOICES=(list(clipboards_groupby.items(),))
        ff=_("Import from Clipboard")

        if request.GET.get('group'):
            req_parameter_group = request.GET.get('group')
            title = f": {req_parameter_group}"
        else:
            req_parameter_group = "Clipboard Home"
            title =  _("Import to Clipboard")

        # if empty clipboards but has group do empty
        if not req_parameter_group in clipboards_groupby:
            clipboards_groupby[req_parameter_group] = ''

        if 'ungroup' in clipboards_groupby :
            len_ungroup = len(clipboards_groupby[req_parameter_group])
        else:
            len_ungroup = 0

        CHOICES=clipboards_groupby[req_parameter_group]
        language= get_language_from_request(request)
        if request.method == 'GET':
            Form = type('ClipboardImportForm', (ClipboardBaseForm,), {
                'clipboard':ChoiceField(
                    choices=CHOICES,
                    label=_("Select Clipboard"),
                    required=False,
                    widget=ClipboardWidget(attrs={"placeholder_ref_id": placeholder_ref_id, "language": language, 'count_target':len_ungroup  }),
                ),
                'title': title,
            })

            Form.Media =type("Media",(), {'css'  : { 'all': ['cascade/css/admin/clipboard.css'] }}) 
            form = Form(request.GET)
            assert form.is_valid()
        elif request.method == 'POST':
            Form = type('ClipboardImportForm', (ClipboardBaseForm,), {
                'clipboard': ChoiceField(
                    choices=CHOICES,
                    label=_("Select Clipboard"),
                    widget=ClipboardWidget(),
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
        if not hasattr(cascade_clipboard, 'data'):
            deserialize_to_clipboard(request, CascadeClipboard.objects.get(identifier=cascade_clipboard).data)
        else:
            deserialize_to_clipboard(request,cascade_clipboard.data)

        # detach plugins from clipboard and reattach them to current placeholder
        cb_placeholder_plugin = request.toolbar.clipboard.cmsplugin_set.first()
        cb_placeholder_instance, _ = cb_placeholder_plugin.get_plugin_instance()

        # bug if the Clipboard Placeholder has alias  'AliasPluginModel', object, it has no attribute 'placeholder_ref',
        # possible need request.toolbar.clipboard.clear() , add .placeholder_ref
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

        qs_clipboards=CascadeClipboardGroup.objects.all()
        if not'Clipboard Home' in list(qs_clipboards.values_list( 'name' , flat=True)):
            qs_clipboards.get_or_create(name="Clipboard Home")

        title = _("Export to Clipboard")
        if request.method == 'GET':
            Form = type('ClipboardExportForm', (ClipboardBaseForm,), {
                'identifier': CharField(required=False),
                'title': title,
                'group' : ModelMultipleChoiceField(
                 queryset=qs_clipboards,
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
                queryset=qs_clipboards,
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


    def populate_static_json(self, filename):
       import os, io, json
       from django.contrib.staticfiles import finders
       clipboard_folder ='cascade/admin/clipboards/'
       path = finders.find(clipboard_folder)
       with io.open(os.path.join(path, filename), 'r') as fh:
            config_data = json.load(fh)
       return config_data

plugin_pool.register_plugin(CascadeClipboardPlugin)
