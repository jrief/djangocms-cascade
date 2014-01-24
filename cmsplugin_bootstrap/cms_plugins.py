# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from cmsplugin_bootstrap import settings

for plugin in settings.BOOTSTRAP_PLUGINS:
    import_module('cmsplugin_bootstrap.plugins.' + plugin)
