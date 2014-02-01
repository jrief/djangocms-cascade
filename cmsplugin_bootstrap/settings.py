# -*- coding: utf-8 -*-
from django.conf import settings

BOOTSTRAP_DEFAULT_BREAKPOINT = getattr(settings, 'BOOTSTRAP_DEFAULT_BREAKPOINT', 'xs')

BOOTSTRAP_PLUGINS = getattr(settings, 'BOOTSTRAP_PLUGINS',
    ('buttons', 'carousel', 'container', 'collapse', 'wrappers',))
