# -*- coding: utf-8 -*-
from django.utils.importlib import import_module


def load_plugins(framework):
    settings = import_module('.{0}.settings'.format(framework), 'cmsplugin_cascade')
    for plugin in getattr(settings, 'CMS_CASCADE_PLUGINS'):
        if '.' in plugin:
            import_module('.{0}'.format(plugin), 'cmsplugin_cascade')
        else:
            import_module('.{0}.{1}'.format(framework, plugin), 'cmsplugin_cascade')
