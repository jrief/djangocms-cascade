# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.conf import settings

try:
    framework = settings.CMS_CASCADE_PLUGINS[0].split('.')[0]
except IndexError:
    framework = ''

for plugin in settings.CMS_CASCADE_PLUGINS:
    import_module('cmsplugin_cascade.' + plugin)
