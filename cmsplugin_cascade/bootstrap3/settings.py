# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

CASCADE_PLUGINS = ('buttons', 'carousel', 'collapse', 'container', 'wrappers', 'image', 'picture',)
CASCADE_TEMPLATE_DIR = getattr(settings, 'CMSPLUGIN_CASCADE_BOOTSTRAP3_TEMPLATE_DIR', 'cascade/bootstrap3')

CASCADE_BOOTSTRAP3_BREAKPOINTS = (
    ('xs', (768, 'mobile-phone', _("mobile phones"), 750)),
    ('sm', (768, 'tablet', _("tablets"), 750)),
    ('md', (992, 'laptop', _("laptops"), 970)),
    ('lg', (1200, 'desktop', _("large desktops"), 1170)),
)
CASCADE_BOOTSTRAP3_GUTTER = getattr(settings, 'CMSPLUGIN_CASCADE_BOOTSTRAP3_GUTTER', 30)
CASCADE_BREAKPOINTS_DICT = dict(tp for tp in CASCADE_BOOTSTRAP3_BREAKPOINTS)
CASCADE_BREAKPOINTS_LIST = list(tp[0] for tp in CASCADE_BOOTSTRAP3_BREAKPOINTS)

CASCADE_BREAKPOINT_APPEARANCES = {
    'xs': {'media': '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0])},
    'sm': {'media': '(min-width: {0}px) and (max-width: {1}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0], CASCADE_BREAKPOINTS_DICT['md'][0])},
    'md': {'media': '(min-width: {0}px) and (max-width: {1}px)'.format(CASCADE_BREAKPOINTS_DICT['md'][0], CASCADE_BREAKPOINTS_DICT['lg'][0])},
    'lg': {'media': '(min-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['lg'][0])},
}
