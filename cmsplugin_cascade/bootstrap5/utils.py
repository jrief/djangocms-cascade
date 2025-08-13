import logging
from django.utils.translation import gettext_lazy as _

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.utils import (compute_aspect_ratio, get_image_size, parse_responsive_length,
   compute_aspect_ratio_with_glossary)

logger = logging.getLogger('cascade')

IMAGE_RESIZE_OPTIONS = [
    ('upscale', _("Upscale image")),
    ('crop', _("Crop image")),
    ('subject_location', _("With subject location")),
    ('high_resolution', _("Optimized for Retina")),
]

IMAGE_SHAPE_CHOICES = [
    ('img-fluid', _("Responsive")),
    ('rounded', _('Rounded')),
    ('rounded-circle', _('Circle')),
    ('img-thumbnail', _('Thumbnail')),
]


def get_image_tags(instance):
    """
    Create a context returning the tags to render an ``<img ...>`` element with
    ``sizes``, ``srcset``, a fallback ``src`` and if required inline styles.
    """
    if hasattr(instance, 'image') and hasattr(instance.image, 'exif'):
        aspect_ratio = compute_aspect_ratio(instance.image)
    elif 'image' in instance.glossary and 'width' in instance.glossary['image']:
        aspect_ratio = compute_aspect_ratio_with_glossary(instance.glossary)
    else:
        # if accessing the image file fails or fake image fails, abort here
        raise FileNotFoundError("Unable to compute aspect ratio of image")

    is_responsive = 'img-fluid' in instance.glossary.get('image_shapes', [])
    resize_options = instance.glossary.get('resize_options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    if 'subject_location' in resize_options and hasattr(instance.image, 'subject_location'):
        subject_location = instance.image.subject_location
    else:
        subject_location = None
    tags = {'sizes': [], 'srcsets': {}, 'is_responsive': is_responsive, 'extra_styles': {}}
    # if is_responsive:
    #     image_width = parse_responsive_length(instance.glossary.get('image_width_responsive') or '100%')
    #     assert(image_width[1]), "The given image has no valid width"
    #     if image_width[1] != 1.0:
    #         tags['extra_styles'].update({'max-width': '{:.0f}%'.format(100 * image_width[1])})
    # else:
    #     image_width = parse_responsive_length(instance.glossary['image_width_fixed'])
    #     if not image_width[0]:
    #         image_width = (instance.image.width, image_width[1])
    try:
        image_height = parse_responsive_length(instance.glossary['image_height'])
    except KeyError:
        image_height = (None, None)
    #if is_responsive:
        for width in app_settings.RESPONSIVE_IMAGE_WIDTHS:
            size = get_image_size(width, image_height, aspect_ratio)
            key = '{0}w'.format(*size)
            tags['srcsets'][key] = {
                'size': size,
                'crop': crop,
                'upscale': upscale,
                'subject_location': subject_location,
            }
        tags['sizes'] = instance.glossary['media_queries'].values()
        # use an existing image as fallback for the <img ...> element
        size = (int(round(width)), int(round(width * aspect_ratio)))
    # else:
    #     size = get_image_size(width, image_height, aspect_ratio)
    #     if 'high_resolution' in resize_options:
    #         tags['srcsets']['1x'] = {'size': size, 'crop': crop, 'upscale': upscale,
    #                                  'subject_location': subject_location}
    #         tags['srcsets']['2x'] = dict(tags['srcsets']['1x'], size=(size[0] * 2, size[1] * 2))
    tags['src'] = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
    return tags
