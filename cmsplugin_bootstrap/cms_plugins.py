# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.importlib import import_module

bootstrap_plugins = ['buttons', 'container', 'thumbnails', 'carousel']

for plugin in getattr(settings, 'CMSPLUGIN_BOOTSTRAP_PLUGINS', bootstrap_plugins):
    import_module('cmsplugin_bootstrap.' + plugin)
