# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.conf import settings

try:
    framework = settings.CMS_CASCADE_PLUGINS[0].split('.')[0]
except IndexError:
    framework = ''

for module in settings.CMS_CASCADE_PLUGINS:
    if '.' in module:
        # the requested plugin was specified with its full name
        import_module('cmsplugin_cascade.' + module)
    else:
        # all plugins from this module shall be imported
        plugin_module = import_module('cmsplugin_cascade.' + module)
        for plugin in plugin_module.all_plugins:
            import_module('cmsplugin_cascade.{0}.{1}'.format(module, plugin))
