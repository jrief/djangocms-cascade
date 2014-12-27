# -*- coding: utf-8 -*-
from django.conf import settings

CMS_CASCADE_PLUGINS = ('grid',)
CMS_CASCADE_LEAF_PLUGINS = getattr(settings, 'CMS_CASCADE_LEAF_PLUGINS', ('TextPlugin', 'FilerImagePlugin',))
