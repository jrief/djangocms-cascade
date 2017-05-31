# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.settings import CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES

CASCADE_PLUGINS = ('buttons', 'carousel', 'accordion', 'container', 'image', 'picture', 'panel')
if 'cms_foundation4' in settings.INSTALLED_APPS:
    CASCADE_PLUGINS += ('secondary_menu',)

CASCADE_FOUNDATION4_BREAKPOINTS = (
    ('small', (40, 'mobile-phone', _("mobile phones"), 40)),
    ('medium', (40.063, 'tablet', _("tablets"), 64)),
    ('large', (64.063, 'laptop', _("laptops"), 90)),
    ('xlarge', (90.063, 'desktop', _("large desktops"), 120)),
)
CASCADE_FOUNDATION4_GUTTER = getattr(settings, 'CMSPLUGIN_CASCADE_FOUNDATION4_GUTTER', 30)
CASCADE_BREAKPOINTS_DICT = dict(tp for tp in CASCADE_FOUNDATION4_BREAKPOINTS)
CASCADE_BREAKPOINTS_LIST = list(tp[0] for tp in CASCADE_FOUNDATION4_BREAKPOINTS)

CASCADE_BREAKPOINT_APPEARANCES = {
    'small': {'media': '(max-width: {0}em)'.format(CASCADE_BREAKPOINTS_DICT['small'][0])},
    'sm': {'media': '(min-width: {0}em) and (max-width: {1}em)'.format(CASCADE_BREAKPOINTS_DICT['medium'][0], CASCADE_BREAKPOINTS_DICT['large'][0])},
    'large': {'media': '(min-width: {0}em) and (max-width: {1}em)'.format(CASCADE_BREAKPOINTS_DICT['large'][0], CASCADE_BREAKPOINTS_DICT['xlarge'][0])},
    'xlarge': {'media': '(min-width: {0}em)'.format(CASCADE_BREAKPOINTS_DICT['xlarge'][0])},
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
