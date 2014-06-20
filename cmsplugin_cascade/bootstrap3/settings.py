# -*- coding: utf-8 -*-
from django.conf import settings

CMS_CASCADE_PLUGINS = ('buttons', 'carousel', 'collapse', 'container', 'wrappers', 'images',)
CMS_CASCADE_TEMPLATE_DIR = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_TEMPLATE_DIR', 'bootstrap3')
CMS_CASCADE_BOOTSTRAP3_BREAKPOINT = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_BREAKPOINT', 'lg')
CMS_CASCADE_LEAF_PLUGINS = getattr(settings, 'CMS_CASCADE_LEAF_PLUGINS', [])

if not 'TextPlugin' in CMS_CASCADE_LEAF_PLUGINS:
    try:
        import djangocms_text_ckeditor
        CMS_CASCADE_LEAF_PLUGINS.append('TextPlugin')
    except ImportError:
        pass
if not 'FilerImagePlugin' in CMS_CASCADE_LEAF_PLUGINS:
    try:
        import filer
        CMS_CASCADE_LEAF_PLUGINS.append('FilerImagePlugin')
    except ImportError:
        pass

CMS_CASCADE_BOOTSTRAP3_BREAKPOINT = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_BREAKPOINT', 'lg')
CMS_CASCADE_BOOTSTRAP3_BREAKPOINTS = {'lg': 1200, 'md': 992, 'sm': 768}
CMS_CASCADE_BOOTSTRAP3_COLUMN_WIDTHS = {'lg': 95, 'md': 78, 'sm': 60, 'xs': 53.3333}
