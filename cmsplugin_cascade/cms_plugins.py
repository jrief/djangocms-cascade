# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from cmsplugin_cascade import settings

for plugin in settings.CASCADE_PLUGINS:
    import_module('cmsplugin_cascade.' + plugin)
