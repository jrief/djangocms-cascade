# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from django.conf import settings


framework = settings.CMS_CASCADE_PLUGINS[0].split('.')[0]

for plugin in settings.CMS_CASCADE_PLUGINS:
    import_module('cmsplugin_cascade.' + plugin)
