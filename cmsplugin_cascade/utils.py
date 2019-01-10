# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import random
import colorsys
 

def remove_duplicates(lst):
    """
    Emulate what a Python ``set()`` does, but keeping the element's order.
    """
    dset = set()
    return [l for l in lst if l not in dset and not dset.add(l)]


def rectify_partial_form_field(base_field, partial_form_fields):
    """
    In base_field reset the attributes label and help_text, since they are overriden by the
    partial field. Additionally, from the list, or list of lists of partial_form_fields
    append the bound validator methods to the given base field.
    """
    base_field.label = ''
    base_field.help_text = ''
    for fieldset in partial_form_fields:
        if not isinstance(fieldset, (list, tuple)):
            fieldset = [fieldset]
        for field in fieldset:
            base_field.validators.append(field.run_validators)

def validate_link(link_data):
    """
    Check if the given model exists, otherwise raise a Validation error
    """
    from django.apps import apps

    try:
        Model = apps.get_model(*link_data['model'].split('.'))
        Model.objects.get(pk=link_data['pk'])
    except Model.DoesNotExist:
        raise ValidationError(_("Unable to link onto '{0}'.").format(Model.__name__))


def compute_aspect_ratio(image):
    if image.exif.get('Orientation', 1) > 4:
        # image is rotated by 90 degrees, while keeping width and height
        return float(image.width) / float(image.height)
    else:
        return float(image.height) / float(image.width)


def compute_aspect_ratio_with_glossary(glossary):
    if glossary['image']['exif_orientation'] > 4:
        # image is rotated by 90 degrees, while keeping width and height
        return float(glossary['image']['width']) / float(glossary['image']['height'])
    else:
        return float(glossary['image']['height']) / float(glossary['image']['width'])


def get_image_size(width, image_height, aspect_ratio):
    if image_height[0]:
        # height was given in px
        return (width, image_height[0])
    elif image_height[1]:
        # height was given in %
        return (width, int(round(width * image_height[1])))
    else:
        # as fallback, adopt height to current width
        return (width, int(round(width * aspect_ratio)))


def parse_responsive_length(responsive_length):
    """
    Takes a string containing a length definition in pixels or percent and parses it to obtain
    a computational length. It returns a tuple where the first element is the length in pixels and
    the second element is its length in percent divided by 100.
    Note that one of both returned elements is None.
    """
    responsive_length = responsive_length.strip()
    if responsive_length.endswith('px'):
        return (int(responsive_length.rstrip('px')), None)
    elif responsive_length.endswith('%'):
        return (None, float(responsive_length.rstrip('%')) / 100)
    return (None, None)


def hsv_to_rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def ramdon_color():
    intcolor = hsv_to_rgb(random.uniform(0.0, 1.0), 0.14, 0.80)
    hsl_css = 'hsl({}, 14%, 80%)'.format( str(random.uniform(0.0, 1.0)))
    return hsl_css
