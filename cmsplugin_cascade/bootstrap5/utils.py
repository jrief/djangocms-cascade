import logging
from django.utils.translation import gettext_lazy as _

from cmsplugin_cascade import app_settings
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
    if is_responsive:
        image_width = parse_responsive_length(instance.glossary.get('image_width_responsive') or '100%')
        assert(image_width[1]), "The given image has no valid width"
        if image_width[1] != 1.0:
            tags['extra_styles'].update({'max-width': '{:.0f}%'.format(100 * image_width[1])})
    else:
        image_width = parse_responsive_length(instance.glossary['image_width_fixed'])
        if not image_width[0]:
            image_width = (instance.image.width, image_width[1])
    try:
        image_height = parse_responsive_length(instance.glossary['image_height'])
    except KeyError:
        image_height = (None, None)
    if is_responsive:
        column_bounds_min = instance.glossary['column_bounds']['min']
        if 'high_resolution' in resize_options:
            column_bounds_max = 2 * instance.glossary['column_bounds']['max']
        else:
            column_bounds_max = instance.glossary['column_bounds']['max']
        num_steps = min(int((column_bounds_max - column_bounds_min) / app_settings.RESPONSIVE_IMAGE_STEP_SIZE),
                        app_settings.RESPONSIVE_IMAGE_MAX_STEPS)
        step_width, max_width = (column_bounds_max - column_bounds_min) / num_steps, 0
        for step in range(0, num_steps + 1):
            width = round(column_bounds_min + step_width * step)
            max_width = max(max_width, width)
            size = get_image_size(width, image_height, aspect_ratio)
            key = '{0}w'.format(*size)
            tags['srcsets'][key] = {'size': size, 'crop': crop, 'upscale': upscale,
                                    'subject_location': subject_location}
        tags['sizes'] = instance.glossary['media_queries'].values()
        # use an existing image as fallback for the <img ...> element
        if not max_width > 0:
            logger.warning('image tags: image max width is zero')
        size = (int(round(max_width)), int(round(max_width * aspect_ratio)))
    else:
        size = get_image_size(image_width[0], image_height, aspect_ratio)
        if 'high_resolution' in resize_options:
            tags['srcsets']['1x'] = {'size': size, 'crop': crop, 'upscale': upscale,
                                     'subject_location': subject_location}
            tags['srcsets']['2x'] = dict(tags['srcsets']['1x'], size=(size[0] * 2, size[1] * 2))
    tags['src'] = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
    return tags


def get_picture_elements(instance):
    """
    Create a context, used to render a <picture> together with all its ``<source>`` elements:
    It returns a list of HTML elements, each containing the information to render a ``<source>``
    element.
    The purpose of this HTML entity is to display images with art directions. For normal images use
    the ``<img>`` element.
    """

    if hasattr(instance, 'image') and hasattr(instance.image, 'exif'):
        aspect_ratio = compute_aspect_ratio(instance.image)
    elif 'image' in instance.glossary and 'width' in instance.glossary['image']:
        aspect_ratio = compute_aspect_ratio_with_glossary(instance.glossary)
    else:
        # if accessing the image file fails or fake image fails, abort here
        logger.warning("Unable to compute aspect ratio of image '{}'".format(instance.image))
        return

    # container_max_heights = instance.glossary.get('container_max_heights', {})
    resize_options = instance.glossary.get('resize_options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    if 'subject_location' in resize_options and hasattr(instance.image, 'subject_location'):
        subject_location = instance.image.subject_location
    else:
        subject_location = None
    max_width = 0
    max_zoom = 0
    elements = []
    for bp, media_query in instance.glossary['media_queries'].items():
        width, media = media_query['width'], media_query['media']
        max_width = max(max_width, width)
        size = None
        try:
            image_height = parse_responsive_length(instance.glossary['responsive_heights'][bp])
        except KeyError:
            image_height = (None, None)
        if image_height[0]:  # height was given in px
            size = (int(width), image_height[0])
        elif image_height[1]:  # height was given in %
            size = (int(width), int(round(width * aspect_ratio * image_height[1])))
        try:
            zoom = int(
                instance.glossary['responsive_zoom'][bp].strip().rstrip('%')
            )
        except (AttributeError, KeyError, ValueError):
            zoom = 0
        max_zoom = max(max_zoom, zoom)
        if size is None:
            # as fallback, adopt height to current width
            size = (int(width), int(round(width * aspect_ratio)))
        elem = {'tag': 'source', 'size': size, 'zoom': zoom, 'crop': crop,
                'upscale': upscale, 'subject_location': subject_location, 'media': media}
        if 'high_resolution' in resize_options:
            elem['size2'] = (size[0] * 2, size[1] * 2)
        elements.append(elem)

    # add a fallback image for old browsers which can't handle the <source> tags inside a <picture> element
    if image_height[1]:
        size = (int(max_width), int(round(max_width * aspect_ratio * image_height[1])))
    else:
        size = (int(max_width), int(round(max_width * aspect_ratio)))
    elements.append({'tag': 'img', 'size': size, 'zoom': max_zoom, 'crop': crop,
                     'upscale': upscale, 'subject_location': subject_location})
    return elements
