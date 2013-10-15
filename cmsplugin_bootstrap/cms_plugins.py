# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.importlib import import_module

plugins = getattr(settings, 'CMSPLUGIN_BOOTSTRAP_PLUGINS', ('buttons', 'container', 'thumbnails'))
for plugin in plugins:
    import_module('cmsplugin_bootstrap.' + plugin)
