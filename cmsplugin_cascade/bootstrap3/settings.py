# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE, orig_config

CASCADE_PLUGINS = ('buttons', 'carousel', 'accordion', 'container', 'image', 'picture', 'panel',
                   'tabs', 'gallery', 'jumbotron')
if 'cms_bootstrap3' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS += ('secondary_menu',)

if 'fluid-lg-width' in orig_config.get('bootstrap3', {}):
    msg = "The configuration directive CMSPLUGIN_CASCADE['bootstrap3']['fluid-lg-width'] in gone"
    warnings.warn(msg)

CMSPLUGIN_CASCADE['bootstrap3'] = {
    'breakpoints': (
        ('xs', (768, 'mobile', _("mobile phones"), 750, 768)),
        ('sm', (768, 'tablet', _("tablets"), 750, 992)),
        ('md', (992, 'laptop', _("laptops"), 970, 1200)),
        ('lg', (1200, 'desktop', _("large desktops"), 1170, 1980)),
    ),
    'gutter': 30,
}
CMSPLUGIN_CASCADE['bootstrap3'].update(orig_config.get('bootstrap3', {}))
for tpl in CMSPLUGIN_CASCADE['bootstrap3']['breakpoints']:
    if len(tpl[1]) != 5:
        msg = "The configuration directive CMSPLUGIN_CASCADE['bootstrap3']['bootstrap3']['{}'] requires 5 parameters"
        raise ImproperlyConfigured(msg.format(tpl[0]))

CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', (
    ('cascade/bootstrap3/secmenu-list-group.html', _("default")),
    ('cascade/bootstrap3/secmenu-unstyled-list.html', _("unstyled")),
))

