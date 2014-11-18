# Django settings for unit test project.
DEBUG = True

SITE_ID = 1

ROOT_URLCONF = 'bs3demo.urls'

SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
    },
}

from cms import __version__ as CMS_VERSION
CMS_VERSION = CMS_VERSION.split('.')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'cmsplugin_cascade',
    'cmsplugin_cascade.sharable',
    'cms',
    'menus',
    int(CMS_VERSION[1]) >= 1 and 'treebeard' or 'mptt',
    'filer',
    'easy_thumbnails',
    'bs3demo.tests',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

# URL that handles the static files served from STATIC_ROOT. Make sure to use a trailing slash.
STATIC_URL = '/static/'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

USE_I18N = False

CMS_TEMPLATES = (
    ('main.html', 'Default Page'),
)

CMS_CASCADE_PLUGINS = ('cmsplugin_cascade.bootstrap3',)

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PRESERVE_EXTENSIONS = True
