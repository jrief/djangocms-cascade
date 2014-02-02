# -*- coding: utf-8 -*-
from django.conf import settings

BOOTSTRAP_DEFAULT_BREAKPOINT = getattr(settings, 'BOOTSTRAP_DEFAULT_BREAKPOINT', 'xs')

CASCADE_PLUGINS = getattr(settings, 'CASCADE_PLUGINS',
    ('bootstrap3.buttons', 'bootstrap3.carousel', 'bootstrap3.container', 'bootstrap3.collapse', 'bootstrap3.wrappers',))
