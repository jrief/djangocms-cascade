# -*- coding: utf-8 -*-
from django.conf import settings

CMS_CASCADE_BOOTSTRAP3_BREAKPOINT = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_BREAKPOINT', 'lg')

if not hasattr(settings, 'CMS_CASCADE_LEAF_PLUGINS'):
    CMS_CASCADE_LEAF_PLUGINS = []
    try:
        import djangocms_text_ckeditor
        CMS_CASCADE_LEAF_PLUGINS.append('TextPlugin')
    except ImportError:
        pass
    try:
        import filer
        CMS_CASCADE_LEAF_PLUGINS.append('FilerImagePlugin')
    except ImportError:
        pass
