# -*- coding: utf-8 -*-
from django.conf import settings

CMS_CASCADE_BOOTSTRAP3_BREAKPOINT = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_BREAKPOINT', 'lg')
CMS_CASCADE_LEAF_PLUGINS = {
    'default': ('TextPlugin', 'FilerImagePlugin',),
}
CMS_CASCADE_LEAF_PLUGINS.update(getattr(settings, 'CMS_CASCADE_LEAF_PLUGINS', {}))
