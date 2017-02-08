# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from collections import OrderedDict
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig
from cmsplugin_cascade.widgets import (
    NumberInputWidget, CascadingSizeWidget, MultipleCascadingSizeWidget, ColorPickerWidget,
    SelectOverflowWidget)


CASCADE_PLUGINS = getattr(settings, 'CMSPLUGIN_CASCADE_PLUGINS', (
    'cmsplugin_cascade.generic',
    'cmsplugin_cascade.icon',
    'cmsplugin_cascade.link',
))

CMSPLUGIN_CASCADE = getattr(settings, 'CMSPLUGIN_CASCADE', {})
orig_config = dict(CMSPLUGIN_CASCADE)

# Incompatibility with djangocms-cascade < version 0.10.x
if not isinstance(CMSPLUGIN_CASCADE.get('plugins_with_extra_fields', {}), dict):
    raise ImproperlyConfigured("CMSPLUGIN_CASCADE['plugins_with_extra_fields'] must be declared as dict.")

CMSPLUGIN_CASCADE.setdefault('alien_plugins', ['TextPlugin'])

# Use a prefix to symbolize a Cascade plugin in case there are ambiguous names.
CMSPLUGIN_CASCADE.setdefault('plugin_prefix', None)

if 'cmsplugin_cascade.extra_fields' in settings.INSTALLED_APPS:
    CMSPLUGIN_CASCADE['plugins_with_extra_fields'] = {
        'BootstrapButtonPlugin': PluginExtraFieldsConfig(),
        'BootstrapRowPlugin': PluginExtraFieldsConfig(),
        'BootstrapJumbotronPlugin': PluginExtraFieldsConfig(
            inline_styles={
                'extra_fields:Paddings': ['padding-top', 'padding-bottom'],
                'extra_units:Paddings': 'px,em'
            }
        ),
        'SimpleWrapperPlugin': PluginExtraFieldsConfig(),
        'HeadingPlugin': PluginExtraFieldsConfig(
            inline_styles={
                'extra_fields:Margins': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
                'extra_units:Margins': 'px,em'
            },
            allow_override=False
        ),
        'HorizontalRulePlugin': PluginExtraFieldsConfig(
            inline_styles={
                'extra_fields:Paddings': ['margin-top', 'margin-bottom'],
                'extra_units:Paddings': 'px,em'
            },
            allow_override=False
        ),
    }
    CMSPLUGIN_CASCADE['plugins_with_extra_fields'].update(
        orig_config.get('plugins_with_extra_fields', {}))
    for plugin, config in CMSPLUGIN_CASCADE['plugins_with_extra_fields'].items():
        if not isinstance(config, PluginExtraFieldsConfig):
            msg = "CMSPLUGIN_CASCADE['plugins_with_extra_fields']['{}'] must instantiate a class of type PluginExtraFieldsConfig"
            raise ImproperlyConfigured(msg.format(plugin))
else:
    CMSPLUGIN_CASCADE['plugins_with_extra_fields'] = {}
"""
With 'plugins_with_extra_fields' we can specify a set of plugins eligible for accepting extra inline
styles.
"""

CMSPLUGIN_CASCADE.setdefault('plugins_with_sharables', {})
CMSPLUGIN_CASCADE['plugins_with_sharables'].setdefault(
    'FramedIconPlugin', ('font_size', 'color', 'background_color', 'text_align', 'border', 'border_radius'),
)

CMSPLUGIN_CASCADE.setdefault('exclude_hiding_plugin', (
    'SegmentPlugin',
))

CMSPLUGIN_CASCADE.setdefault('link_plugin_classes', (
    'cmsplugin_cascade.link.plugin_base.DefaultLinkPluginBase',
    'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
    'cmsplugin_cascade.link.forms.LinkForm',
))
"""
3-Tuple containing shared base classes for classes wishing to link onto something:
1. Base class for a CMSPlugin, 2. A Model Mixin, 3. The base class used to build the form.
"""

CMSPLUGIN_CASCADE.setdefault('plugins_with_bookmark', [
    'SimpleWrapperPlugin', 'HeadingPlugin'])

CMSPLUGIN_CASCADE.setdefault('bookmark_prefix', '')

CMSPLUGIN_CASCADE['extra_inline_styles'] = OrderedDict((
    ('Margins', (('margin-top', 'margin-right', 'margin-bottom', 'margin-left',), MultipleCascadingSizeWidget)),
    ('Paddings', (('padding-top', 'padding-right', 'padding-bottom', 'padding-left',), MultipleCascadingSizeWidget)),
    ('Widths', (('min-width', 'width', 'max-width',), MultipleCascadingSizeWidget)),
    ('Heights', (('min-height', 'height', 'max-height',), MultipleCascadingSizeWidget)),
    ('Font Size', (('font-size',), MultipleCascadingSizeWidget)),
    ('Line Height', (('line-height',), NumberInputWidget)),
    ('Colors', (('color', 'background-color',), ColorPickerWidget)),
    ('Overflow', (('overflow', 'overflow-x', 'overflow-y',), SelectOverflowWidget)),
))
CMSPLUGIN_CASCADE['extra_inline_styles'].update(orig_config.get('extra_inline_styles', {}))

CMSPLUGIN_CASCADE.setdefault('segmentation_mixins', [
    ('cmsplugin_cascade.segmentation.mixins.EmulateUserModelMixin', 'cmsplugin_cascade.segmentation.mixins.EmulateUserAdminMixin')
])

CMSPLUGIN_CASCADE.setdefault('plugins_with_extra_render_templates', {
    'TextLinkPlugin': (
        ('cascade/link/text-link.html', _("default")),
        ('cascade/link/text-link-linebreak.html', _("with line break")),
    )
})

CMSPLUGIN_CASCADE.setdefault('allow_plugin_hiding', False)
"""
Add a checkbox to each named plugin, which if checked hides that plugin during the rendering phase.
Useful to temporarily deactivate plugins, instead of removing them.
"""

# Folder where extracted icon fonts are stored.
CMSPLUGIN_CASCADE.setdefault('icon_font_root',
                             os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'icon_fonts')))

CSS_PREFIXES = {
    'image_set': ['-webkit-image-set', '-moz-image-set', '-o-image-set', '-ms-image-set', 'image-set'],
}
