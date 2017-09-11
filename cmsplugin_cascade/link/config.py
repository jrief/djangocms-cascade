# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.module_loading import import_string

from cmsplugin_cascade import app_settings


LinkPluginBase, LinkElementMixin, LinkForm = (import_string(cls)
    for cls in app_settings.CMSPLUGIN_CASCADE['link_plugin_classes'])
