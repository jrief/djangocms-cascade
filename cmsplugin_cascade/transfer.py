from cmsplugin_cascade.models import CascadeElement

from djangocms_timed_publishing.models import TimedPublishingInterval


def export_plugin_data(plugin, plugin_data):
    """
    Export the plugin data to a JSON file and return it as a response.
    """
    if isinstance(plugin, CascadeElement):
        return plugin_data


def import_plugin_data(plugin, plugin_data):
    """
    Import the plugin data from a JSON file and update the plugin instance.
    """
    if isinstance(plugin, CascadeElement):
        return plugin.save()
