# -*- coding: utf-8 -*-
from django.conf import settings

CASCADE_PLUGIN_DEPENDENCIES = {
    'cascade/js/ring.js': 'cascade/js/underscore.js',
    'cascade/js/admin/sharableglossary.js': 'cascade/js/ring.js',
    'cascade/js/admin/linkplugin.js': 'cascade/js/ring.js',
    'cascade/js/admin/sharablelinkplugin.js': ('cascade/js/admin/linkplugin.js', 'cascade/js/admin/sharableglossary.js',),
    'cascade/js/admin/simplelinkplugin.js': 'cascade/js/admin/linkplugin.js',
    'cascade/js/admin/imageplugin.js': ('cascade/js/admin/linkplugin.js', 'cascade/js/admin/sharableglossary.js',),
    'cascade/js/admin/pictureplugin.js': ('cascade/js/admin/linkplugin.js', 'cascade/js/admin/sharableglossary.js',),
}
CASCADE_PLUGIN_DEPENDENCIES.update(getattr(settings, 'CMSPLUGIN_CASCADE_DEPENDENCIES', {}))
