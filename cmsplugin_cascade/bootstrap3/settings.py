# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

CMS_CASCADE_PLUGINS = ('buttons', 'carousel', 'collapse', 'container', 'wrappers', 'picture',)
CMS_CASCADE_TEMPLATE_DIR = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_TEMPLATE_DIR', 'cascade/bootstrap3')
CMS_CASCADE_LEAF_PLUGINS = list(getattr(settings, 'CMS_CASCADE_LEAF_PLUGINS', ()))

if 'TextPlugin' not in CMS_CASCADE_LEAF_PLUGINS:
    try:
        import djangocms_text_ckeditor as unused
        CMS_CASCADE_LEAF_PLUGINS.append('TextPlugin')
    except ImportError:
        pass
# if not 'FilerImagePlugin' in CMS_CASCADE_LEAF_PLUGINS:
#     try:
#         import filer
#         CMS_CASCADE_LEAF_PLUGINS.append('FilerImagePlugin')
#     except ImportError:
#         pass

CMS_CASCADE_BOOTSTRAP3_BREAKPOINTS = (
    ('xs', (768, 'mobile-phone', _("mobile phones"), 750)),
    ('sm', (768, 'tablet', _("tablets"), 970)),
    ('md', (992, 'laptop', _("laptops"), 1170)),
    ('lg', (1200, 'desktop', _("large desktops"), 1170)),
)
CASCADE_BOOTSTRAP3_GUTTER = getattr(settings, 'CMS_CASCADE_BOOTSTRAP3_GUTTER', 30)

CASCADE_BREAKPOINTS_DICT = dict(tp for tp in CMS_CASCADE_BOOTSTRAP3_BREAKPOINTS)
CASCADE_BREAKPOINTS_LIST = list(tp[0] for tp in CMS_CASCADE_BOOTSTRAP3_BREAKPOINTS)
CASCADE_BREAKPOINT_APPEARANCES = {
    'xs': {'media': '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0])},
    'sm': {'media': '(min-width: {0}px) and (max-width: {1}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0], CASCADE_BREAKPOINTS_DICT['md'][0])},
    'md': {'media': '(min-width: {0}px) and (max-width: {1}px)'.format(CASCADE_BREAKPOINTS_DICT['md'][0], CASCADE_BREAKPOINTS_DICT['lg'][0])},
    'lg': {'media': '(min-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['lg'][0])},
}
