# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

CASCADE_PLUGIN_DEPENDENCIES = {
    'cascade/js/ring.js': 'cascade/js/underscore.js',
    'cascade/js/admin/sharableglossary.js': 'cascade/js/ring.js',
    'cascade/js/admin/linkpluginbase.js': ('cascade/js/admin/sharableglossary.js',),
    'cascade/js/admin/linkplugin.js': ('cascade/js/admin/linkpluginbase.js',),
    'cascade/js/admin/imageplugin.js': ('cascade/js/admin/linkpluginbase.js',),
    'cascade/js/admin/pictureplugin.js': ('cascade/js/admin/linkpluginbase.js',),
}
CASCADE_PLUGIN_DEPENDENCIES.update(getattr(settings, 'CMSPLUGIN_CASCADE_DEPENDENCIES', {}))
CASCADE_PLUGINS_WITH_EXTRAFIELDS = getattr(settings, 'CMSPLUGIN_CASCADE_WITH_EXTRAFIELDS', []) \
    if 'cmsplugin_cascade.extra_fields' in settings.INSTALLED_APPS else []
CASCADE_PLUGINS_WITH_SHARABLES = getattr(settings, 'CMSPLUGIN_CASCADE_WITH_SHARABLES', {}) \
    if 'cmsplugin_cascade.sharable' in settings.INSTALLED_APPS else {}
