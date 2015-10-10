# Django settings for unit test project.
import os
import sys
from .utils import find_django_migrations_module

DEBUG = True

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

SITE_ID = 1

ROOT_URLCONF = 'bs3demo.urls'

SECRET_KEY = 'secret'

import django

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}
if django.VERSION[:2] > (1, 6):
    DATABASES['default'].update({'NAME': 'sqlite17.db'})
else:
    DATABASES['default'].update({'NAME': 'sqlite16.db'})

from cms import __version__ as CMS_VERSION
CMS_VERSION = tuple(int(n) for n in CMS_VERSION.split('.')[:2])

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'djangocms_admin_style',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'reversion',
    'djangocms_text_ckeditor',
    'django_select2',
    'cmsplugin_cascade',
    'cmsplugin_cascade.extra_fields',
    'cmsplugin_cascade.sharable',
    'cms',
    'cms_bootstrap3',
    'menus',
    CMS_VERSION >= (3, 1) and 'treebeard' or 'mptt',
    'filer',
    'easy_thumbnails',
    'sekizai',
    'bs3demo',
)
if django.VERSION[:2] >= (1, 7):
    MIGRATION_MODULES = {
        'cms': find_django_migrations_module('cms'),
        'menus': find_django_migrations_module('menus'),
        'djangocms_text_ckeditor': find_django_migrations_module('djangocms_text_ckeditor'),
        'cmsplugin_cascade': find_django_migrations_module('cmsplugin_cascade'),
    }
else:
    INSTALLED_APPS += ('south',)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
)

# silence false-positive warning 1_6.W001
# https://docs.djangoproject.com/en/1.8/ref/checks/#backwards-compatibility
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Absolute path to the directory that holds media.
if django.VERSION[:2] > (1, 6):
    MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
else:
    MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media16')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

# URL that handles the static files served from STATIC_ROOT. Make sure to use a trailing slash.
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.abspath(os.path.join(PROJECT_DIR, os.pardir, os.pardir, 'bower_components')),
)


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors':  (
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                'django.core.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'cms.context_processors.cms_settings',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.request',
            ),
        },
    },
]



# List of callables that know how to import templates from various sources.




# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

LANGUAGES = (
    ('en-us', 'English'),
)

#############################################################
# Application specific settings

if sys.argv[1] == 'test':
    CMS_TEMPLATES = (
         ('testing.html', 'Default Page'),
    )
else:
    CMS_TEMPLATES = (
         ('main.html', 'Main Content Container'),
         ('wrapped.html', 'Wrapped Bootstrap Column'),
    )

CMS_SEO_FIELDS = True

CMS_CACHE_DURATIONS = {
    'content': 3600,
    'menus': 3600,
    'permissions': 86400,
}

CMS_PLACEHOLDER_CONF = {
    'Main Content Container': {
        'plugins': ['BootstrapContainerPlugin'],
    },
}

CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.link', 'cmsplugin_cascade.bootstrap3',)

CMSPLUGIN_CASCADE_WITH_EXTRAFIELDS = [
    'BootstrapButtonPlugin', 'BootstrapContainerPlugin',
    'BootstrapColumnPlugin', 'BootstrapRowPlugin', 'BootstrapPicturePlugin',
    'SimpleWrapperPlugin',
]

CMSPLUGIN_CASCADE_WITH_SHARABLES = {
    'BootstrapImagePlugin': ('image-shapes', 'image-width-responsive', 'image-width-fixed', 'image-height', 'resize-options',),
    'BootstrapPicturePlugin': ('image-shapes', 'responsive-heights', 'image-size', 'resize-options',),
    'BootstrapButtonPlugin': ('link',),
    'TextLinkPlugin': ('link', 'target',),
}

COLUMN_GLOSSARY = {
    'breakpoints': ['xs', 'sm', 'md', 'lg'],
    'container_max_widths': {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170},
    'fluid': False,
    'media_queries': {
        'xs': ['(max-width: 768px)'],
        'sm': ['(min-width: 768px)', '(max-width: 992px)'],
        'md': ['(min-width: 992px)', '(max-width: 1200px)'],
        'lg': ['(min-width: 1200px)'],
    },
}

CMS_PLACEHOLDER_CONF = {
    'Bootstrap Column': {
        'plugins': ['BootstrapRowPlugin', 'TextPlugin'],
        'parent_classes': {'BootstrapRowPlugin': []},
        'require_parent': False,
        'glossary': COLUMN_GLOSSARY,
    },
}

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'skin': 'moono',
    'toolbar': 'CMS',
}

FILER_ALLOW_REGULAR_USERS_TO_ADD_ROOT_FOLDERS = True

FILER_DUMP_PAYLOAD = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    #'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_HIGH_RESOLUTION = False

THUMBNAIL_PRESERVE_EXTENSIONS = True

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/opt/local/bin/optipng {filename}',
    'gif': '/opt/local/bin/optipng {filename}',
    'jpeg': '/opt/local/bin/jpegoptim {filename}',
}

#THUMBNAIL_DEBUG = True
