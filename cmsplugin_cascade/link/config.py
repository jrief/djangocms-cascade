from django.utils.module_loading import import_string
from cmsplugin_cascade import app_settings


LinkPluginBase, LinkFormMixin = (import_string(cls)
    for cls in app_settings.CMSPLUGIN_CASCADE['link_plugin_classes'])
