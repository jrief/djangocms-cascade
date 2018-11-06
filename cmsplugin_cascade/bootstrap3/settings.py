# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig


CASCADE_PLUGINS = ['buttons', 'carousel', 'accordion', 'container', 'image', 'picture',
                   'panel', 'tabs', 'gallery', 'jumbotron']
if 'cms_bootstrap' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS.append('secondary_menu')


def set_defaults(config):
    config.setdefault('bootstrap3', {})
    config['bootstrap3'].setdefault(
        'breakpoints', (
            ('xs', (768, 'mobile', _("mobile phones"), 750, 768)),
            ('sm', (768, 'tablet', _("tablets"), 750, 992)),
            ('md', (992, 'laptop', _("laptops"), 970, 1200)),
            ('lg', (1200, 'desktop', _("large desktops"), 1170, 1980)),))
    for tpl in config['bootstrap3']['breakpoints']:
        if len(tpl[1]) != 5:
            msg = "The configuration directive CMSPLUGIN_CASCADE['bootstrap3']['bootstrap3']['{}'] requires 5 parameters"
            raise ImproperlyConfigured(msg.format(tpl[0]))

    config['bootstrap3'].setdefault('gutter', 30)

    config['plugins_with_extra_fields'].setdefault('BootstrapButtonPlugin', PluginExtraFieldsConfig())
    config['plugins_with_extra_fields'].setdefault('BootstrapRowPlugin', PluginExtraFieldsConfig())
    config['plugins_with_extra_fields'].setdefault('BootstrapJumbotronPlugin', PluginExtraFieldsConfig(
        inline_styles={
            'extra_fields:Paddings': ['margin-top', 'margin-bottom', 'padding-top', 'padding-bottom'],
            'extra_units:Paddings': 'px,em'
        }
    ))
    config['plugins_with_extra_fields'].setdefault('HeadingPlugin', PluginExtraFieldsConfig(
        inline_styles={
            'extra_fields:Margins': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
            'extra_units:Margins': 'px,em'
        },
        allow_override=False
    ))

    config['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', (
        ('cascade/bootstrap3/secmenu-list-group.html', _("List Group")),
        ('cascade/bootstrap3/secmenu-unstyled-list.html', _("Unstyled List")),))

    if os.getenv('DJANGO_CLIENT_FRAMEWORK', '').startswith('angular'):
        config['bootstrap3']['template_basedir'] = 'angular-ui'
