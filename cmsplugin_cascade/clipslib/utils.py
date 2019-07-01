from cms.api import add_plugin
from cms.utils import get_language_from_request
from cms.models.placeholderpluginmodel import PlaceholderReference
from djangocms_transfer.datastructures import ArchivedPlaceholder, ArchivedPlugin
#from djangocms_transfer.forms import  _get_parsed_data

def _object_version_data_hook_cascade(data, for_page=False):
    if not data:
        return data
    if 'plugin_type' in data:
        return ArchivedPlugin(**data)
    return data


def _get_parsed_data_cascade(file_obj, for_page=False):
    import io
    import json

    with io.open(file_obj, encoding='utf-8-sig') as json_data:
        raw = json_data
        return json.load(raw, object_hook=_object_version_data_hook_cascade)


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

