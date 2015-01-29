# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


for module in getattr(settings, 'CMSPLUGIN_CASCADE_PLUGINS', []):
    try:
        # if a module was specified, load all plugins in module settings
        module_settings = import_module('{0}.settings'.format(module))
        module_plugins = getattr(module_settings, 'CASCADE_PLUGINS', [])
        for p in module_plugins:
            try:
                import_module('{0}.{1}'.format(module, p))
            except ImportError as err:
                raise ImproperlyConfigured("Plugin {0} as specified in {1}.settings.CMSPLUGIN_CASCADE_PLUGINS "
                                           "could not be loaded: {2}".format(p, module, err.message))
    except ImportError:
        try:
            # otherwise try with cms_plugins in the named module
            import_module('{0}.cms_plugins'.format(module))
        except ImportError:
            # otherwise just use the named module as plugin
            import_module('{0}'.format(module))
