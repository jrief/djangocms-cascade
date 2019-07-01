from django.conf import settings

if getattr(settings, 'CASCADE_CLIPS_LIBRARY', None):
    import json
    from django.http import JsonResponse, HttpResponse
    from django.contrib.staticfiles import finders
    from django.views import View
    from djangocms_transfer.importer import import_plugins
    from django.shortcuts import render
    from cmsplugin_cascade import app_settings
    from cms.models import Placeholder
    from cms.utils import get_language_from_request
    from cmsplugin_cascade.clipboard.library.utils import _deserialize_to_clipboard, _get_parsed_data_cascade
    from django.contrib.auth.decorators import login_required

    from cmsplugin_cascade.cms_toolbars import CascadeToolbar

    try:
        from cms.toolbar.utils import get_plugin_tree_as_json
    except BaseException:
        from cmsplugin_cascade.clipslib.utils_backport_cms34 import get_plugin_tree_as_json

    class CascadeCopyToClipboard(View):
        template_name = "cascade/admin/library_clips/clipboard_cascade.html"

        def post(self, request, *args, **kwargs):

            for k, v in enumerate(app_settings.CASCADE_CLIPBOARD_LIBRARY):
                for g, r in v.items():
                    if request._post.get('paramater'):
                        relative_path_clipboard = request._post.get(
                            'paramater')
                        path = finders.find(relative_path_clipboard)
                        data = _get_parsed_data_cascade(path)
            language = get_language_from_request(request)
            if 'plugins' in data:
                if 'plugins' == next(iter(data)):
                    _deserialize_to_clipboard(request, data)

                # Placeholder plugins import
                placeholder = request.toolbar.clipboard
                tree_order = placeholder.get_plugin_tree_order(
                    'en', parent_id=request.toolbar.clipboard.pk)
                data['plugin_order'] = tree_order + ['__COPY__']
                data['target_placeholder_id'] = placeholder.pk
                #context = {'structure_data': json.dumps(data)}
            else:
                import_plugins(
                    plugins=data,
                    placeholder=Placeholder.objects.all()[0],
                    language=language,
                    root_plugin_id=None
                )
            data_plug = json.loads(
                get_plugin_tree_as_json(
                    request,
                    request.toolbar.clipboard.get_plugins_list()))

            data = {
                "plugin_id": request.toolbar.clipboard.cmsplugin_set.first().pk,
                "placeholder_id": request.toolbar.clipboard.pk,
                "type": "plugin",
                "plugin_order": ['__COPY__'],
                "plugin_type": "PlaceholderPlugin",
                "plugin_parent": "None",
                "move_a_copy": True,
                "html": data_plug['html'],
                "data": data_plug}
            return JsonResponse(data)

    @login_required
    def CascadeLibClipsFolder(request, pk=None):
        context = {'folder_id': str(pk)}
        context.update(
            {'clips': app_settings.CASCADE_CLIPBOARD_LIBRARY[0],
             'csrf': request.toolbar.csrf_token()})
        return HttpResponse(
            render(
                request,
                "cascade/admin/library_clips/folder_clips.html",
                context))

    @login_required
    def CascadeLibClips(request, pk=None,):
        if not pk:
            pk = 1
        context = {'folder_id': str(pk), 'folder_name': app_settings.CASCADE_CLIPBOARD_LIBRARY[0][str(
            pk)]['folder_name'], 'title_clips': "Clipboard Library"}
        context.update({'clips': app_settings.CASCADE_CLIPBOARD_LIBRARY[0]})
        return HttpResponse(
            render(
                request,
                "cascade/admin/library_clips/library_clips.html",
                context))
