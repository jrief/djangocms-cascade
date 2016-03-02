# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE, orig_config

CASCADE_PLUGINS = ('buttons', 'carousel', 'accordion', 'container', 'image', 'picture', 'panel',
                   'tabs', 'gallery',)
if 'cms_bootstrap3' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS += ('secondary_menu',)

CMSPLUGIN_CASCADE['bootstrap3'] = {
    'breakpoints': (
        ('xs', (768, 'mobile-phone', _("mobile phones"), 750)),
        ('sm', (768, 'tablet', _("tablets"), 750)),
        ('md', (992, 'laptop', _("laptops"), 970)),
        ('lg', (1200, 'desktop', _("large desktops"), 1170)),
    ),
    'gutter': 30,
    'fluid-lg-width': 1980,
}
CMSPLUGIN_CASCADE['bootstrap3'].update(orig_config.get('bootstrap3', {}))

CMSPLUGIN_CASCADE['plugins_with_extra_render_templates'].setdefault('BootstrapSecondaryMenuPlugin', (
    ('cascade/bootstrap3/secmenu-list-group.html', _("default")),
    ('cascade/bootstrap3/secmenu-unstyled-list.html', _("unstyled")),
))
