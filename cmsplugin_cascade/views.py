from cmsplugin_cascade.clipboard.admin import CascadeClipboardAdmin

from django.contrib.staticfiles.templatetags.staticfiles import static


from jsonfield.fields import JSONField
from djangocms_text_ckeditor.models import Text
from djangocms_text_ckeditor.utils import plugin_tags_to_id_list, replace_plugin_tags

import io
import json
import os
from django.http import HttpResponseRedirect

from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.models import Text
from djangocms_text_ckeditor.utils import plugin_tags_to_id_list, replace_plugin_tags
from cms.api import add_plugin
from cmsplugin_cascade.models import CascadeElement

from cms.api import add_plugin
from cms.models.placeholderpluginmodel import PlaceholderReference
from cms.plugin_pool import plugin_pool
from cms.utils import get_language_from_request
from django.http import JsonResponse
from django.http import HttpResponse
from cms.models import CMSPlugin, Placeholder

from django.contrib.staticfiles import finders

from django.views import View

from django.http import HttpResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.shortcuts import redirect

from django.template import RequestContext


from djangocms_transfer.datastructures import ArchivedPlaceholder, ArchivedPlugin
#from djangocms_transfer.forms import  _object_version_data_hook, _get_parsed_data
from djangocms_transfer.importer import import_plugins

from django.shortcuts import render
from cmsplugin_cascade import app_settings

from cmsplugin_cascade import app_settings
from cms.utils.urlutils import admin_reverse
from django.contrib.staticfiles import finders

from djangocms_transfer import  helpers
import json
from cms.toolbar.utils import get_plugin_tree_as_json
from cmsplugin_cascade.cms_toolbars import CascadeToolbar

def _object_version_data_hook(data, for_page=False):
    if not data:
        return data
    if 'pluginfs' in data:
        return ArchivedPlaceholder(
            slot=data['placeholder'],
            plugins=data['plugins'],
        )

    if 'plugin_type' in data:
        return ArchivedPlugin(**data)
    return data


def _get_parsed_data(file_obj, for_page=False):
    import io

    with io.open(file_obj, encoding='utf-8-sig') as json_data:
        raw = json_data
        return json.load(raw, object_hook=_object_version_data_hook)


def _deserialize_to_clipboard(request, data):
    """
    Restore clipboard by creating plugins from given data.
    """
    parent = None

    def plugins_from_data(placeholder, parent, data):
        language = 'en'
        for plugin_type, data, children_data in data:

            plugin_class = plugin_pool.get_plugin(plugin_type)

            kwargs = dict(data)

            inlines = kwargs.pop('inlines', [])
            shared_glossary = kwargs.pop('shared_glossary', None)
            instance = add_plugin(
                placeholder,
                plugin_class,
                language,
                target=parent,
                **kwargs)

            if isinstance(instance, CascadeElement):
                instance.plugin_class.add_inline_elements(instance, inlines)
                instance.plugin_class.add_shared_reference(
                    instance, shared_glossary)

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

    if hasattr(request, 'toolbar'):
        clipboard = request.toolbar.clipboard
        try:
            clipboard.cmsplugin_set.first().delete()
        except BaseException:
            pass

        ref_plugin = clipboard.cmsplugin_set.first()

        if ref_plugin is None:
            # the clipboard is empty
            root_plugin = add_plugin(
                clipboard,
                'PlaceholderPlugin',
                language,
                name='clipboard')
        else:
            # remove old entries from the clipboard
            try:
                root_plugin = ref_plugin.cms_placeholderreference
            except PlaceholderReference.DoesNotExist:
                root_plugin = add_plugin(
                    clipboard, 'PlaceholderPlugin', language, name='clipboard')
            else:
                inst = ref_plugin.get_plugin_instance()[0]
                inst.placeholder_ref.get_plugins().delete()
        if 'plugins' in data:
            data = data['plugins']
        plugins_from_data(root_plugin.placeholder_ref, None, data)

class CascadeCopyToClipboard(View):
    template_name = "cascade/admin/library_clips/clipboard_cascade.html"

    def post(self, request, *args, **kwargs):

        for k, v in enumerate(app_settings.CASCADE_CLIPBOARD_LIBRARY):
            for g, r in v.items():
                if request._post.get('paramater'):
                    relative_path_clipboard = request._post.get('paramater')
                    path = finders.find(relative_path_clipboard)
                    data = _get_parsed_data(path)
        language = get_language_from_request(request)
        if 'plugins' in data:
            if 'plugins' == next(iter(data)):
                _deserialize_to_clipboard(request, data)

            # Placeholder plugins import
            placeholder=request.toolbar.clipboard
            tree_order = placeholder.get_plugin_tree_order('en', parent_id=request.toolbar.clipboard.pk)
            data['plugin_order'] = tree_order + ['__COPY__']
            data['target_placeholder_id'] = placeholder.pk
            context = {'structure_data': json.dumps(data)}
        else:
            import_plugins(
                plugins=data,
                placeholder=Placeholder.objects.all()[0],
                language=language,
                root_plugin_id=None
            )
        data_plug = json.loads(get_plugin_tree_as_json(request, request.toolbar.clipboard.get_plugins_list()))
        
        data = {
            "plugin_id": request.toolbar.clipboard.cmsplugin_set.first().pk,
            "placeholder_id": request.toolbar.clipboard.pk,
            "type": "plugin",
            "plugin_order": ['__COPY__'],
            "plugin_type": "PlaceholderPlugin",
            "plugin_parent": "None",
            "move_a_copy": True,
            
            "html":  data_plug['html'],
            "data": data_plug
        }

        return JsonResponse(data)


def CascadeLibClipsFolder(request, pk=None):
    context = {'folder_id': str(pk) }
    context.update({'clips': app_settings.CASCADE_CLIPBOARD_LIBRARY[0], 'csrf': request.toolbar.csrf_token() })

    return HttpResponse(
        render(
            request,
            "cascade/admin/library_clips/folder_clips.html",
            context))

def CascadeLibClips(request, pk=None,):
    if not pk:
        pk = 1
    context = {'folder_id': str(pk),'folder_name':app_settings.CASCADE_CLIPBOARD_LIBRARY[0][str(pk)]['folder_name'], 'title_clips':    CascadeToolbar.clips_title }
    context.update({'clips': app_settings.CASCADE_CLIPBOARD_LIBRARY[0]})
    return HttpResponse(
        render(
            request,
            "cascade/admin/library_clips/library_clips.html",
            context))
