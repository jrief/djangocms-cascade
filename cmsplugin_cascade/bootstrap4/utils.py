# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from cmsplugin_cascade.utils import compute_aspect_ratio, get_image_size, parse_responsive_length

logger = logging.getLogger('cascade')


def get_image_tags(context, instance):
    """
    Create a context returning the tags to render an <img ...> element:
    ``sizes``, ``srcset``, a fallback ``src`` and if required inline styles.
    """
    try:
        aspect_ratio = compute_aspect_ratio(instance.image)
    except Exception as e:
        # if accessing the image file fails, abort here
        return
    is_responsive = 'img-responsive' in instance.glossary.get('image_shapes', [])
    resize_options = instance.glossary.get('resize_options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    subject_location = instance.image.subject_location and 'subject_location' in resize_options
    resolutions = (False, True) if 'high_resolution' in resize_options else (False,)
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
        max_width = 0
        for bp in instance.glossary['breakpoints']:
            if bp not in instance.glossary['container_max_widths']:
                continue
            width = int(image_width[1] * instance.glossary['container_max_widths'][bp])
            max_width = max(max_width, width)
            size = get_image_size(width, image_height, aspect_ratio)
            if bp in instance.glossary['media_queries']:
                tags['sizes'].append('{0} {1}px'.format(' and '.join(instance.glossary['media_queries'][bp]), width))
            for high_res in resolutions:
                if high_res:
                    size = (size[0] * 2, size[1] * 2)
                key = '{0}w'.format(size[0])
                tags['srcsets'][key] = {'size': size, 'crop': crop, 'upscale': upscale,
                                        'subject_location': subject_location}
        # use an existing image as fallback for the <img ...> element
        if not max_width > 0:
            logger.warning('image tags: image max width is zero')
        size = (int(round(max_width)), int(round(max_width * aspect_ratio)))
    else:
        size = get_image_size(image_width[0], image_height, aspect_ratio)
        if len(resolutions) > 1:
            for high_res in resolutions:
                if high_res:
                    tags['srcsets']['2x'] = {'size': (size[0] * 2, size[1] * 2), 'crop': crop,
                        'upscale': upscale, 'subject_location': subject_location}
                else:
                    tags['srcsets']['1x'] = {'size': size, 'crop': crop,
                        'upscale': upscale, 'subject_location': subject_location}
    tags['src'] = {'size': size, 'crop': crop, 'upscale': upscale,
                   'subject_location': subject_location}
    return tags
