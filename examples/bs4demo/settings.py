# Django settings for unit test project.
from __future__ import unicode_literals

import os
import sys


from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig
from django.utils.text import format_lazy

DEBUG = True

BASE_DIR = os.path.dirname(__file__)

# Root directory for this Django project
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.path.pardir))

# Directory where working files, such as media and databases are kept
WORK_DIR = os.path.join(PROJECT_ROOT, 'workdir')
if not os.path.isdir(WORK_DIR):
    os.makedirs(WORK_DIR)

SITE_ID = 1

ROOT_URLCONF = 'bs4demo.urls'

SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(WORK_DIR, 'db.sqlite3'),
    },
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    #'reversion',
    'djangocms_text_ckeditor',
    'django_select2',
    'cmsplugin_cascade',
    'cmsplugin_cascade.clipboard',
    'cmsplugin_cascade.extra_fields',
    'cmsplugin_cascade.icon',
    'cmsplugin_cascade.sharable',
    'cmsplugin_cascade.segmentation',
    'cms',
    'cms_bootstrap',
    'adminsortable2',
    'menus',
    'treebeard',
    'filer',
    'easy_thumbnails',
    'sass_processor',
    'sekizai',
    'bs4demo',
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]



# silence false-positive warning 1_6.W001
# https://docs.djangoproject.com/en/1.8/ref/checks/#backwards-compatibility
#TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(WORK_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(WORK_DIR, 'static')

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

STATICFILES_DIRS = [
    ('node_modules', os.path.join(PROJECT_ROOT, 'node_modules')),
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': (
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.template.context_processors.csrf',
            'django.template.context_processors.request',
            'django.contrib.messages.context_processors.messages',
            'sekizai.context_processors.sekizai',
            'cms.context_processors.cms_settings',
            'bs4demo.context_processors.cascade',
        ),
    },
}]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse',
         }
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s %(module)s] %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

#############################################################
# Application specific settings

if sys.argv[1] == 'test':
    CMS_TEMPLATES = (
         ('testing.html', "Default Page"),
    )
else:
    CMS_TEMPLATES = (
         ('bs4demo/main.html', "Main Content"),
         ('bs4demo/wrapped.html', "Wrapped Bootstrap Column"),
    )

CMS_SEO_FIELDS = True

CMS_CACHE_DURATIONS = {
    'content': 3600,
    'menus': 3600,
    'permissions': 86400,
}

CMSPLUGIN_CASCADE_PLUGINS = (
    'cmsplugin_cascade.segmentation',
    'cmsplugin_cascade.generic',
    'cmsplugin_cascade.leaflet',
    'cmsplugin_cascade.link',
    'cmsplugin_cascade.bootstrap4',
    'bs4demo',
)

CMSPLUGIN_CASCADE = {
    'alien_plugins': ('TextPlugin', 'TextLinkPlugin',),
    'plugins_with_sharables': {
        'BootstrapImagePlugin': ('image_shapes', 'image_width_responsive', 'image_width_fixed',
                                 'image_height', 'resize_options',),
        'BootstrapPicturePlugin': ('image_shapes', 'responsive_heights', 'image_size', 'resize_options',),
    },
    'exclude_hiding_plugin': ('SegmentPlugin', 'Badge'),
    'allow_plugin_hiding': True,
    'leaflet': {'default_position': {'lat': 50.0, 'lng': 12.0, 'zoom': 6}},
    'cache_strides': True,
    'plugins_with_extra_fields': {
        'SimpleWrapperPlugin': PluginExtraFieldsConfig(
            inline_styles={
                'extra_fields:Colors': ['color', 'background-color'],
                'extra_fields:Margins': ['margin-top', 'margin-right', 'margin-botton,', 'margin-left'],
                'extra_units:Margins': 'px,em',
            },
            html_tag_attributes={
                'extra_fields:HtmlAttrs': [
                    ('Animate-on-scroll', {
                        'data-aos': {
                           'widget_choices_list': ["inherit", "fade", "fade-up", "fade-down", "fade-left", "fade-right", "fade-up-right", "fade-up-left", "fade-down-right", "fade-down-left", "flip-up", "flip-down", "flip-left", "flip-right", "slide-up", "slide-down", "slide-left", "slide-right", "zoom-in", "zoom-in-up", "zoom-in-down", "zoom-in-left", "zoom-in-right", "zoom-out", "zoom-out-up", "zoom-out-down", "zoom-out-left", "zoom-out-right"],
                           'widget_attrs': {'title': 'Animation name'},
                        },
                        'data-aos-offset': {
                           'widget_choices_list': ["inherit"] + [i for i in range(-500, 510, 10)],
                           'widget_attrs': {'title': 'Optional: Change offset to trigger animations sooner or later (px)'},
                        },
                        'data-aos-duration': {
                           'widget_choices_list': ["inherit"] + [i for i in range(0, 2100, 200)],
                           'widget_attrs': {'title': 'Optional: Duration of animation (ms)', 'style': '', },
                                           },
                        'data-aos-easing': {
                           'widget_choices_list': ["inherit", "linear", "ease", "ease-in", "ease-out", "ease-in-out", "ease-in-back", "ease-out-back", "ease-in-out-back", "ease-in-sine", "ease-out-sine", "ease-in-out-sine", "ease-in-quad", "ease-out-quad", "ease-in-out-quad", "ease-in-cubic", "ease-out-cubic", "ease-in-out-cubic", "ease-in-quart", "ease-out-quart", "ease-in-out-quart"],
                           'widget_attrs': {'title': 'Optional: Choose timing function to ease elements in different ways'}
                                         },
                        'data-aos-delay': {
                           'widget_choices_list': ["inherit"] + [i for i in range(0, 2100, 200)],
                           'widget_attrs': {'title': 'Optional: Delay animation (ms)'}
                                        },
                        'data-aos-anchor': {
                           'widget_choices_cms_page_anchors': [],
                           'widget_attrs': {'title': 'Optional: Anchor element, whose offset will be counted to trigger animation instead of actual elements offset', },
                                            },
                        'data-aos-anchor-placement': {
                           'widget_choices_list': ["inherit", "top-bottom", "top-center", "top-top", "center-bottom", "center-center", "center-top", "bottom-bottom", "bottom-center", "bottom-top"],
                           'widget_attrs': {'title': 'Optional: Anchor placement - which one position of element on the screen should trigger animation'},
                                                   },
                        'data-aos-once': {
                           'widget_choices_list': ['inherit', 'true', 'false'],
                           'widget_attrs': {'title': 'Optional: Choose wheter animation should fire once, or every time you scroll up/down to element'},
                                          },
                     }
                     ),
                    ('Bootstrap-Scrollspy', {
                        'data-spy': {
                           'widget_choices_list': ["inherit", "scroll"],
                           'widget_attrs': {'title': 'Automatically update Bootstrap navigation or list group components based on scroll position to indicate which link is currently active in the viewport.', 'style': '', },
                        },
                        'data-target': {
                           'widget_choices_cms_page_anchors': [],
                           'widget_attrs': {'title': 'Anchors', 'style': '', },
                        },
                        'data-offset': {
                           'widget_choices_list': ["inherit"] + [i for i in range(-500, 510, 10)],
                           'widget_attrs': {'title': 'offset', 'style': '', },
                        },
                    }),
                ],
            },
        ),
    }
}

CMS_PLACEHOLDER_CONF = {
    # this placeholder is used in templates/main.html, it shows how to
    # scaffold a djangoCMS page starting with an empty placeholder
    'Main Content': {
        'plugins': ['BootstrapContainerPlugin', 'BootstrapJumbotronPlugin'],
        'parent_classes': {'BootstrapContainerPlugin': None, 'BootstrapJumbotronPlugin': None},
    },
    # this placeholder is used in templates/wrapped.html, it shows how to
    # add content to an existing Bootstrap column
    'Bootstrap Column': {
        'plugins': ['BootstrapRowPlugin', 'TextPlugin', ],
        'parent_classes': {'BootstrapRowPlugin': None},
        'require_parent': False,
    },
}

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'skin': 'moono-lisa',
    'toolbar': 'CMS',
    'stylesSet': format_lazy('default:{}', reverse_lazy('admin:cascade_texteditor_config')),
}

SELECT2_CSS = 'node_modules/select2/dist/css/select2.min.css'
SELECT2_JS = 'node_modules/select2/dist/js/select2.min.js'

FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True

FILER_DUMP_PAYLOAD = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_HIGH_RESOLUTION = False

THUMBNAIL_PRESERVE_EXTENSIONS = True

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/opt/local/bin/optipng {filename}',
    'gif': '/opt/local/bin/optipng {filename}',
    'jpeg': '/opt/local/bin/jpegoptim {filename}',
}

SASS_PROCESSOR_INCLUDE_DIRS = [
    os.path.join(PROJECT_ROOT, 'node_modules'),
]

SASS_PROCESSOR_ROOT = STATIC_ROOT

# to access files such as fonts via staticfiles finders
NODE_MODULES_URL = STATIC_URL + 'node_modules/'

try:
    from .private_settings import *
except ImportError:
    pass

