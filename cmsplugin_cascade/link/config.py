# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string


LinkPluginBase, LinkElementMixin, LinkForm = (import_string(cls)
    for cls in settings.CMSPLUGIN_CASCADE['link_plugin_classes'])
