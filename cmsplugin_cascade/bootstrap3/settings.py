# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


CASCADE_PLUGINS = ['buttons', 'carousel', 'accordion', 'container', 'image', 'picture',
                   'panel', 'tabs', 'gallery', 'jumbotron']
if 'cms_bootstrap3' in settings.INSTALLED_APPS:
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

    config['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', (
        ('cascade/bootstrap3/secmenu-list-group.html', _("List Group")),
        ('cascade/bootstrap3/secmenu-unstyled-list.html', _("Unstyled List")),))

    if os.getenv('DJANGO_CLIENT_FRAMEWORK', '').startswith('angular'):
        config['bootstrap3']['template_basedir'] = 'angular-ui'
