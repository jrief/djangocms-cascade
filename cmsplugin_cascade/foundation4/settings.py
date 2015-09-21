# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.settings import CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES

CASCADE_PLUGINS = ('buttons', 'carousel', 'accordion', 'container', 'image', 'picture', 'panel')
if 'cms_foundation4' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS += ('secondary_menu',)

CASCADE_FOUNDATION4_BREAKPOINTS = (
    ('xs', (768, 'mobile-phone', _("mobile phones"), 750)),
    ('sm', (768, 'tablet', _("tablets"), 750)),
    ('md', (992, 'laptop', _("laptops"), 970)),
    ('lg', (1200, 'desktop', _("large desktops"), 1170)),
)
CASCADE_FOUNDATION4_GUTTER = getattr(settings, 'CMSPLUGIN_CASCADE_FOUNDATION4_GUTTER', 30)
CASCADE_BREAKPOINTS_DICT = dict(tp for tp in CASCADE_FOUNDATION4_BREAKPOINTS)
CASCADE_BREAKPOINTS_LIST = list(tp[0] for tp in CASCADE_FOUNDATION4_BREAKPOINTS)

CASCADE_BREAKPOINT_APPEARANCES = {
    'xs': {'media': '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0])},
    'sm': {'media': '(min-width: {0}px) and (max-width: {1}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0], CASCADE_BREAKPOINTS_DICT['md'][0])},
    'md': {'media': '(min-width: {0}px) and (max-width: {1}px)'.format(CASCADE_BREAKPOINTS_DICT['md'][0], CASCADE_BREAKPOINTS_DICT['lg'][0])},
    'lg': {'media': '(min-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['lg'][0])},
}

CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES.setdefault('CarouselPlugin', (  # @UndefinedVariable
    ('cascade/foundation4/carousel.html', _("default")),
    ('cascade/foundation4/angular-ui/carousel.html', "angular-ui"),
))
CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES.setdefault('FoundationAccordionPlugin', (  # @UndefinedVariable
    ('cascade/foundation4/accordion.html', _("default")),
    ('cascade/foundation4/angular-ui/accordion.html', "angular-ui"),
))
CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES.setdefault('FoundationSecondaryMenuPlugin', (  # @UndefinedVariable
    ('cascade/foundation4/secmenu-list-group.html', _("default")),
    ('cascade/foundation4/secmenu-unstyled-list.html', _("unstyled")),
))
