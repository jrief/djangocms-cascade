# -*- coding: utf-8 -*-
from tempfile import mkdtemp

gettext = lambda s: s

HELPER_SETTINGS = dict(
    INSTALLED_APPS=[
        'jsonfield',
        'reversion',
        'filer',
        'easy_thumbnails',
        'djangocms_text_ckeditor',
        'cmsplugin_cascade',
        'cmsplugin_cascade.extra_fields',
        'cmsplugin_cascade.sharable',
    ],
    LANGUAGE_CODE='en',
    LANGUAGES=(
        ('en', 'English'),
    ),
    CMS_TEMPLATES=(
        ('testing.html', 'Default Page'),
    ),
    CMSPLUGIN_CASCADE_PLUGINS=(
        'cmsplugin_cascade.link',
        'cmsplugin_cascade.bootstrap3',
    ),
    CMSPLUGIN_CASCADE_WITH_EXTRAFIELDS=[
        'BootstrapButtonPlugin', 'BootstrapContainerPlugin',
        'BootstrapColumnPlugin', 'BootstrapRowPlugin',
        'BootstrapPicturePlugin', 'SimpleWrapperPlugin',
    ],
    CMSPLUGIN_CASCADE_WITH_SHARABLES={
        'BootstrapImagePlugin': (
            'image-shapes',
            'image-width-responsive',
            'image-width-fixed',
            'image-height',
            'resize-options',
        ),
        'BootstrapPicturePlugin': (
            'image-shapes',
            'responsive-heights',
            'image-size',
            'resize-options',
        ),
        'BootstrapButtonPlugin': ('link',),
        'TextLinkPlugin': ('link', 'target',),
    },
    CMS_PLACEHOLDER_CONF={
        'Main Content Container': {
            'plugins': ['BootstrapContainerPlugin'],
        },
        'Bootstrap Column': {
            'plugins': ['BootstrapRowPlugin', 'TextPlugin'],
            'parent_classes': {'BootstrapRowPlugin': []},
            'require_parent': False,
            'glossary': {
                'breakpoints': ['xs', 'sm', 'md', 'lg'],
                'container_max_widths': {
                    'xs': 750,
                    'sm': 750,
                    'md': 970,
                    'lg': 1170
                },
                'fluid': False,
                'media_queries': {
                    'xs': ['(max-width: 768px)'],
                    'sm': ['(min-width: 768px)', '(max-width: 992px)'],
                    'md': ['(min-width: 992px)', '(max-width: 1200px)'],
                    'lg': ['(min-width: 1200px)'],
                },
            },
        },
    },
    THUMBNAIL_PROCESSORS=(
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    THUMBNAIL_PRESERVE_EXTENSIONS=True,
    THUMBNAIL_OPTIMIZE_COMMAND={
        'png': '/opt/local/bin/optipng {filename}',
        'gif': '/opt/local/bin/optipng {filename}',
        'jpeg': '/opt/local/bin/jpegoptim {filename}',
    },
)


def run():
    from djangocms_helper import runner
    runner.cms('cmsplugin_cascade')

if __name__ == "__main__":
    run()
