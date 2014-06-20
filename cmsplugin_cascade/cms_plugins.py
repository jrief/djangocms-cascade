# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


for module in getattr(settings, 'CMS_CASCADE_PLUGINS'):
    try:
        # if a module was specified, load all plugins in module settings
        module_settings = import_module('.{0}.settings'.format(module), 'cmsplugin_cascade')
        module_plugins = getattr(module_settings, 'CMS_CASCADE_PLUGINS', [])
        for p in module_plugins:
            try:
                import_module('.{0}.{1}'.format(module, p), 'cmsplugin_cascade')
            except ImportError:
                raise ImproperlyConfigured("Plugin {0} as specified in {1}.settings.CMS_CASCADE_PLUGINS could not be loaded".format(p, module))
    except ImportError:
        try:
            # otherwise try with cms_plugins in the named module
            import_module('.{0}.cms_plugins'.format(module), 'cmsplugin_cascade')
        except ImportError:
            # otherwise just use the named module as plugin
            import_module('.{0}'.format(module), 'cmsplugin_cascade')
