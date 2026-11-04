from django.contrib.admin import site as default_admin_site
from django.contrib import messages
from django.utils.translation import get_language_from_request

from cms.api import add_plugin
from cms.models.placeholderpluginmodel import PlaceholderReference
from cms.plugin_pool import plugin_pool
from cms.toolbar.utils import get_toolbar_from_request
from cmsplugin_cascade.models import CascadeElement


def serialize_from_placeholder(placeholder, admin_site=default_admin_site):
    """
    Create a serialized representation of all the plugins belonging to the clipboard.
    """
    def populate_data(parent, data):
        for child in plugin_qs.filter(parent=parent).order_by('position'):
            instance, plugin = child.get_plugin_instance(admin_site)
            plugin_type = plugin.__class__.__name__
            entry = (plugin_type, plugin.get_data_representation(instance), [])
            data.append(entry)
            populate_data(child, entry[2])

    data = {'plugins': []}
    plugin_qs = placeholder.cmsplugin_set.all()
    populate_data(None, data['plugins'])
    return data


def deserialize_to_clipboard(request, data):
    """
    Restore clipboard's content by creating plugins from given data.
    """
    def plugins_from_data(placeholder, parent, data):
        for plugin_type, data, children_data in data:
            try:
                plugin_class = plugin_pool.get_plugin(plugin_type)
            except Exception:
                messages.add_message(request, messages.ERROR, "Unable create plugin of type: {}".format(plugin_type))
                continue
            kwargs = dict(data)
            inlines = kwargs.pop('inlines', [])
            shared_glossary = kwargs.pop('shared_glossary', None)
            try:
                instance = add_plugin(placeholder, plugin_class, language, target=parent, **kwargs)
            except Exception:
                msg = "Unable to create plugin of type: {} with data: {}".format(plugin_type, kwargs)
                messages.add_message(request, messages.ERROR, msg)
                continue
            assert isinstance(instance, CascadeElement)
            # instance.plugin_class.add_inline_elements(instance, inlines)
            # instance.plugin_class.add_shared_reference(instance, shared_glossary)

            # for some unknown reasons add_plugin sets instance.numchild to 0,
            # but fixing and save()-ing 'instance' executes some filters in an unwanted manner
            plugins_from_data(placeholder, instance, children_data)

    language = get_language_from_request(request, check_path=True)
    clipboard = request.toolbar.clipboard
    clipboard = get_toolbar_from_request(request).clipboard
    ref_plugin = clipboard.cmsplugin_set.first()
    if ref_plugin is None:
        # the clipboard is empty
        root_plugin = add_plugin(clipboard, 'PlaceholderPlugin', language, name='clipboard')
    else:
        # remove old entries from the clipboard
        try:
            root_plugin = ref_plugin.cms_placeholderreference
        except PlaceholderReference.DoesNotExist:
            root_plugin = add_plugin(clipboard, 'PlaceholderPlugin', language, name='clipboard')
        else:
            inst, _ = ref_plugin.get_plugin_instance()
            inst.placeholder_ref.get_plugins().delete()
    plugins_from_data(root_plugin.placeholder_ref, None, data['plugins'])
