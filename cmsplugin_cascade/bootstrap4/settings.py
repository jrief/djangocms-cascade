# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig
from .grid import Breakpoint, Bound


CASCADE_PLUGINS = ['accordion', 'card', 'carousel', 'container', 'image', 'jumbotron', 'picture', 'tabs']
if 'cms_bootstrap' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS.append('secondary_menu')


def set_defaults(config):
    config.setdefault('bootstrap4', {})
    config['bootstrap4'].setdefault(
        'default_bounds', {
            Breakpoint.xs: Bound(320, 572),
            Breakpoint.sm: Bound(540, 540),
            Breakpoint.md: Bound(720, 720),
            Breakpoint.lg: Bound(960, 960),
            Breakpoint.xl: Bound(1140, 1140),
        })
    config['bootstrap4'].setdefault(
        'fluid_bounds', {
            Breakpoint.xs: Bound(320, 576),
            Breakpoint.sm: Bound(576, 768),
            Breakpoint.md: Bound(768, 992),
            Breakpoint.lg: Bound(992, 1200),
            Breakpoint.xl: Bound(1200, 1980),
        })
    config['bootstrap4'].setdefault('gutter', 30)

    config['plugins_with_extra_fields'].setdefault('BootstrapButtonPlugin', PluginExtraFieldsConfig())
    config['plugins_with_extra_fields'].setdefault('BootstrapRowPlugin', PluginExtraFieldsConfig())
    config['plugins_with_extra_fields'].setdefault('BootstrapJumbotronPlugin', PluginExtraFieldsConfig(
        inline_styles={
            'extra_fields:Paddings': ['margin-top', 'margin-bottom', 'padding-top', 'padding-bottom'],
            'extra_units:Paddings': 'px,em'
        }
    ))

    config['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', [
        ('cascade/bootstrap4/secmenu-list-group.html', _("List Group")),
        ('cascade/bootstrap4/secmenu-unstyled-list.html', _("Unstyled List"))
    ])
