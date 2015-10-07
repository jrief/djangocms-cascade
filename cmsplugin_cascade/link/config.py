# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.module_loading import import_string

LinkPluginBase, LinkElementMixin, LinkForm = [import_string(cls)
    for cls in getattr(settings, 'CMSPLUGIN_CASCADE_LINKPLUGIN_CLASSES', (
        'cmsplugin_cascade.link.plugin_base.LinkPluginBase',
        'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
        'cmsplugin_cascade.link.forms.LinkForm',
    ))
]
"""
Tuple containing shared base classes for classes wishing to link onto something:
1. Base class for a CMSPlugin, 2. A Model Mixin, 3. The base class used to build the form.
"""
