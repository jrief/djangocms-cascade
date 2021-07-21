from django.utils.text import format_lazy
from django.urls import reverse_lazy

from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig


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

ROOT_URLCONF = 'tests.urls'

SECRET_KEY = 'test'

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'DIRS': ['tests/templates'],
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
        )
    }
}]


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'filer',
    'easy_thumbnails',
    'treebeard',
    'menus',
    'sekizai',
    'cms',
    'adminsortable2',
    'djangocms_text_ckeditor',
    'django_select2',
    'cmsplugin_cascade',
    'cmsplugin_cascade.clipboard',
    'cmsplugin_cascade.extra_fields',
    'cmsplugin_cascade.icon',
    'cmsplugin_cascade.sharable',
    'cmsplugin_cascade.segmentation',
    'tests',
]


USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
]

LANGUAGE_CODE = 'en'

CMS_TEMPLATES = [
    ('testing.html', 'Default Page'),
]

CMSPLUGIN_CASCADE_PLUGINS = [
    'cmsplugin_cascade.link',
    'cmsplugin_cascade.bootstrap4',
]


CMSPLUGIN_CASCADE = {
    'plugins_with_extra_fields': {
        'BootstrapButtonPlugin': PluginExtraFieldsConfig(),
        'BootstrapContainerPlugin': PluginExtraFieldsConfig(),
        'BootstrapColumnPlugin': PluginExtraFieldsConfig(),
        'BootstrapRowPlugin': PluginExtraFieldsConfig(),
        'BootstrapPicturePlugin': PluginExtraFieldsConfig(),
        'SimpleWrapperPlugin': PluginExtraFieldsConfig(),
    },
    'plugins_with_sharables': {
        'BootstrapImagePlugin': (
            'image_shapes',
            'image_width_responsive',
            'image_width_fixed',
            'image_height',
            'resize_options',
        ),
        'BootstrapPicturePlugin': (
            'image_shapes',
            'responsive_heights',
            'image_size',
            'resize_options',
        ),
    },
}

CMS_PLACEHOLDER_CONF = {
    'Main Content': {
        'plugins': ['BootstrapContainerPlugin'],
        'parent_classes': {
            'BootstrapContainerPlugin': None,
            'TextLinkPlugin': ['TextPlugin'],
        },
    },
}

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_PRESERVE_EXTENSIONS = True,

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/opt/local/bin/optipng {filename}',
    'gif': '/opt/local/bin/optipng {filename}',
    'jpeg': '/opt/local/bin/jpegoptim {filename}',
}

CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'skin': 'moono',
    'toolbar': 'CMS',
    'toolbar_HTMLField': [
        ['Undo', 'Redo'],
        ['cmsplugins', '-', 'ShowBlocks'],
        ['Format', 'Styles'],
        ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
        ['Maximize', ''],
        '/',
        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '-', 'RemoveFormat'],
        ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
        ['HorizontalRule'],
        ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Table'],
        ['Source']
    ],
    'stylesSet': format_lazy('default:{}', reverse_lazy('admin:cascade_texteditor_config')),
}

SILENCED_SYSTEM_CHECKS = ['2_0.W001']
