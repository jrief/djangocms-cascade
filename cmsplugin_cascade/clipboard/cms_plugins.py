import json
from ast import literal_eval
from django.conf.urls import url
from django.contrib.admin import site as default_admin_site
from django.contrib.admin.helpers import AdminForm
from django.core.exceptions import PermissionDenied
from django.forms import CharField, ModelChoiceField, ModelMultipleChoiceField, ChoiceField, MultipleChoiceField
from django.http import HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import now
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
from django.conf import settings


def FormViewClipboard(request, form, context):
    group_selected=request.GET.get('group', 'Clipboard Home')
    widget = form['clipboard'].field.widget
    widget.attrs['id']= '1'
    widget.attrs['pk']= '1'
   # widget.choices, len_ungroup =  merder()
    form['clipboard'].field.widget.get_context('clipboards', '',   widget.attrs)
    widget.optgroups = form['clipboard'].field.widget.optgroups_result
    tpl_basedir = settings.CMSPLUGIN_CASCADE['bootstrap4'].get('template_basedir', None)
    context.update( {
           'img_or_pic_lost_pk': settings.CMSPLUGIN_CASCADE['fallback']['img_or_pic_lost_pk'],
           'tpl_basedir' :tpl_basedir,
           'len_ungroup' :form.len_ungroup,
           'group_selected' : group_selected,
           'widget': widget ,
           'placeholder_ref_id': request.GET['placeholder'],
           'language_ref': request.GET['language'],
           'main_scss': settings.CMSPLUGIN_CASCADE['fallback']['path_main_scss'],
            'qs_clipboards': CascadeClipboard.objects.all(),
            'groups_exclude_home':list(CascadeClipboardGroup.objects.all().exclude( name='Clipboard Home').values_list('name',flat=True,)),
            'widget_optgroups':  form['clipboard'].field.widget.optgroups_result,
              'form': form })
    return render(request, "cascade/admin/clipboard_import.html", context)


def tree_group_clipboards():
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

        [treegroup( groups, index) for index, groups in enumerate(queryset , start=1)]
        if 'ungroup' in clipboards_groupby :
            len_ungroup = len(clipboards_groupby['ungroup'])
        else:
            len_ungroup = 0
        if not 'Clipboard Home' in clipboards_groupby:
            group ='Clipboard Home'
            clipboard_home = CascadeClipboardGroup.objects.get_or_create(name=group)
        CHOICES = (list(clipboards_groupby.items(),))
        return CHOICES, len_ungroup


class ClipboardWidget(widgets.Select):

    def __init__(self, *args, **kwargs):
        self.req= None
        self.optgroups_result= None
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super(ClipboardWidget, self).get_context(name, value, attrs)
        context['request'] = self.req
        self.optgroups_result = self.optgroups(name, context['widget']['value'], attrs)
        groups=list(CascadeClipboardGroup.objects.all().exclude( name='Clipboard Home').values_list('name',flat=True))
        context['groups_exclude_home'] = groups
        context['qs_clipboards'] = CascadeClipboard.objects.all()
        context['main_scss'] = settings.CMSPLUGIN_CASCADE['fallback']['path_main_scss']
        
        return context


class CascadeClipboardPlugin(CMSPluginBase):
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
                action='modal',
                attributes={
                    'icon': 'import',
                },
            ),
        ]

    def render_modal_window(self, request,form):
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
        if not  'ClipboardExportForm' in  str(type(form)):
            context.update({ 
                'main_scss': settings.CMSPLUGIN_CASCADE['fallback']['path_main_scss'],
                'qs_clipboards': CascadeClipboard.objects.all(),
                'groups_exclude_home':list(CascadeClipboardGroup.objects.all().exclude( name='Clipboard Home').values_list('name',flat=True)),
                 'group_selected' : 'Clipboard Home',
            })
            response = FormViewClipboard(request, form , context )
            return response
        else:
            return TemplateResponse(request, self.change_form_template, context )
        
        return TemplateResponse(request, self.change_form_template, context )


    def import_plugins_view(self, request, *args, **kwargs):
        # TODO: check for permissions
        view_breakdown = request.session.get('view_breakdown', "lg")
        placeholder_ref_id = None
        if request.GET.get('placeholder'):
            placeholder_ref_id = request.GET.get('placeholder')
        if request.GET.get('group'):
            req_parameter_group = request.GET.get('group')
            title = ": {}".format(req_parameter_group)
        else:
            req_parameter_group = "Clipboard Home"
            title =  _("Import to Clipboard")
        CHOICES, len_ungroup = tree_group_clipboards()

        language= get_language_from_request(request)
       
        if request.method == 'GET':
            Form = type('ClipboardImportForm', (ClipboardBaseForm,), {
                'clipboard':ChoiceField(
                    choices=CHOICES,
                    label=_("Select Clipboard"),
                    required=False,
                    widget=ClipboardWidget(attrs={"placeholder_ref_id": placeholder_ref_id, "language": language, 'count_target':len_ungroup ,'view_breakdown':view_breakdown  }),
                ),
                'title': title,
            })

            Form.Media = type("Media",(), {'css'  : { 'all': [ ''] }})
            Form.base_fields['clipboard'].widget.req = request
            form = Form(request.GET)
            form.len_ungroup = len_ungroup
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

            complete_form_dict = {'placeholder':request.GET['placeholder'], 'language':request.GET['language'] }
            request_post_dict = request.POST.dict()
            request_post_dict.update(complete_form_dict)
            form = Form(request_post_dict)

            form.len_ungroup = len_ungroup
            if form.is_valid():
                return self.paste_from_clipboard(request, form)
        return self.render_modal_window(request, form)

    def paste_from_clipboard(self, request, form):
    #    request.toolbar.clipboard.clear()
        placeholder = form.cleaned_data['placeholder']
        language = form.cleaned_data['language']
        cascade_clipboard = form.cleaned_data['clipboard']

        tree_order = placeholder.get_plugin_tree_order(language)
        if not hasattr(cascade_clipboard, 'data'):
            cascade_clipboard = CascadeClipboard.objects.get(identifier=cascade_clipboard)
        if settings.CMSPLUGIN_CASCADE.get('fallback', None ).get('img_or_pic_lost_pk', None):
           tree_data_lost_ref_img = str(cascade_clipboard.data).replace("'image_file': {'model': 'filer.image', 'pk': ", "'image_file': {'model': 'filer.image', 'pk': 10000")
           cascade_clipboard.data= literal_eval(tree_data_lost_ref_img)
        deserialize_to_clipboard(request, cascade_clipboard.data)
        cascade_clipboard.last_accessed_at = now()
        cascade_clipboard.save(update_fields=['last_accessed_at'])

        # detach plugins from clipboard and reattach them to current placeholder
        cb_placeholder_plugin = request.toolbar.clipboard.cmsplugin_set.first()
        cb_placeholder_instance, _ = cb_placeholder_plugin.get_plugin_instance()

        # bug if cb_placeholder_instance.plugin_type == 'Alias or Text,
        #  they don't have a 'placeholder ref' attribute.
        if cb_placeholder_instance.plugin_type == 'AliasPlugin' or cb_placeholder_instance.plugin_type ==  'AliasPluginModel' or cb_placeholder_instance.plugin_type == 'TextPlugin':
            return HttpResponse('Clipboard has AliasPlugin or TextPlugin, clear Clipboard Before')
        else:
            new_plugins = cb_placeholder_instance.placeholder_ref.get_plugins()
        new_plugins.update(placeholder=placeholder)

        # reorder root plugins in placeholder
        root_plugins = placeholder.get_plugins(language).filter(parent__isnull=True).order_by('changed_date')
        for position, plugin in enumerate(root_plugins.iterator()):
            plugin.update(position=position)

        placeholder.mark_as_dirty(language, clear_cache=False)
        # create a list of pasted plugins to be added to the soptgroups_resultture view
        all_plugins = placeholder.get_plugins(language)
        if all_plugins.exists():
            new_plugins = placeholder.get_plugins(language).exclude(pk__in=tree_order)
            data = json.loads(get_plugin_tree_as_json(request, list(new_plugins)))
            data['plugin_order'] = tree_order + ['__COPY__']
        else:
            return render(request, 'cascade/admin/clipboard_reload_page.html')
        data['target_placeholder_id'] = placeholder.pk
        context = {'soptgroups_resultture_data': json.dumps(data)}
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
        data = serialize_from_placeholder(placeholder,language=language)
        cascade_clipboard = CascadeClipboard.objects.create(
            identifier=identifier,
            data=data,
        )
        cascade_clipboard.group.set(group) 
        return render(request, 'cascade/admin/clipboard_close_frame.html', {})

plugin_pool.register_plugin(CascadeClipboardPlugin)
