# Django settings for unit test project.
import os

DEBUG = True

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

SITE_ID = 1

ROOT_URLCONF = 'bootstrap3.urls'

SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sqlite',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'cmsplugin_cascade',
    'cms',
    'menus',
    'mptt',
    'bootstrap3',
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
#     'cms.middleware.page.CurrentPageMiddleware',
#     'cms.middleware.user.CurrentUserMiddleware',
#     'cms.middleware.toolbar.ToolbarMiddleware',
#     'cms.middleware.language.LanguageCookieMiddleware',
)

# Absolute path to the directory that holds media.
#MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
#MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

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

TEMPLATE_DIRS = (
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
#USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
#USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
#USE_TZ = True

LANGUAGES = (
    ('en', 'English'),
)
