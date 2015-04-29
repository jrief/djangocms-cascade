# -*- coding: utf-8 -*-
from __future__ import unicode_literals
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.conf import settings
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget, ColorPickerWidget, SelectOverflowWidget

CASCADE_DEFAULT_PARENT_CLASSES = () + \
    ('SegmentPlugin',) if 'cmsplugin_cascade.segmentation' in settings.INSTALLED_APPS else ()

CASCADE_ALIEN_PLUGINS = list(getattr(settings, 'CMSPLUGIN_CASCADE_ALIEN_PLUGINS', ('TextPlugin',)))

CASCADE_PLUGIN_DEPENDENCIES = {
    'cascade/js/ring.js': 'cascade/js/underscore.js',
    'cascade/js/admin/sharableglossary.js': 'cascade/js/ring.js',
    'cascade/js/admin/segmentplugin.js': 'cascade/js/ring.js',
    'cascade/js/admin/linkpluginbase.js': ('cascade/js/admin/sharableglossary.js',),
    'cascade/js/admin/linkplugin.js': ('cascade/js/admin/linkpluginbase.js',),
    'cascade/js/admin/imageplugin.js': ('cascade/js/admin/linkpluginbase.js',),
    'cascade/js/admin/pictureplugin.js': ('cascade/js/admin/linkpluginbase.js',),
}
CASCADE_PLUGIN_DEPENDENCIES.update(getattr(settings, 'CMSPLUGIN_CASCADE_DEPENDENCIES', {}))

CASCADE_PLUGINS_WITH_EXTRAFIELDS = getattr(settings, 'CMSPLUGIN_CASCADE_WITH_EXTRAFIELDS', (
    'BootstrapButtonPlugin',
    'BootstrapRowPlugin',
    'SimpleWrapperPlugin',
    'HorizontalRulePlugin',
)) if 'cmsplugin_cascade.extra_fields' in settings.INSTALLED_APPS else ()

CASCADE_PLUGINS_WITH_SHARABLES = getattr(settings, 'CMSPLUGIN_CASCADE_WITH_SHARABLES', {
}) if 'cmsplugin_cascade.sharable' in settings.INSTALLED_APPS else {}

CASCADE_EXTRA_INLINE_STYLES = getattr(settings, 'CMSPLUGIN_CASCADE_EXTRA_INLINE_STYLES', OrderedDict((
    ('Margins', (('margin-top', 'margin-right', 'margin-bottom', 'margin-left',), MultipleCascadingSizeWidget)),
    ('Paddings', (('padding-top', 'padding-right', 'padding-bottom', 'padding-left',), MultipleCascadingSizeWidget)),
    ('Widths', (('min-width', 'width', 'max-width',), MultipleCascadingSizeWidget)),
    ('Heights', (('min-height', 'height', 'max-height',), MultipleCascadingSizeWidget)),
    ('Colors', (('color', 'background-color',), ColorPickerWidget)),
    ('Overflow', (('overflow', 'overflow-x', 'overflow-y',), SelectOverflowWidget)),
)))

CASCADE_SEGMENTATION_MIXINS = getattr(settings, 'CMSPLUGIN_CASCADE_SEGMENTATION_MIXINS', (
    'cmsplugin_cascade.segmentation.mixins.EmulateUserMixin',
))
