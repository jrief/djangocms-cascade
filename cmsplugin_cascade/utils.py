# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings

from django.core.exceptions import ValidationError
from django.contrib.staticfiles.finders import get_finders
from django.utils.translation import ugettext_lazy as _

try:
    from django.utils.functional import keep_lazy_text
except ImportError:
    # backported from Django-1.10
    # TODO: remove when dropping support for Django-1.9
    from django.utils import six
    from django.utils.functional import lazy, wraps, Promise

    def keep_lazy(*resultclasses):
        if not resultclasses:
            raise TypeError("You must pass at least one argument to keep_lazy().")

        def decorator(func):
            lazy_func = lazy(func, *resultclasses)

            @wraps(func)
            def wrapper(*args, **kwargs):
                for arg in list(args) + list(six.itervalues(kwargs)):
                    if isinstance(arg, Promise):
                        break
                else:
                    return func(*args, **kwargs)
                return lazy_func(*args, **kwargs)

            return wrapper

        return decorator

    def keep_lazy_text(func):
        return keep_lazy(six.text_type)(func)

@keep_lazy_text
def format_lazy(format_string, *args, **kwargs):
    return format_string.format(*args, **kwargs)


def remove_duplicates(lst):
    """
    Emulate what a Python ``set()`` does, but keeping the element's order.
    """
    dset = set()
    return [l for l in lst if l not in dset and not dset.add(l)]


def resolve_dependencies(filenames):
    """
    Given a filename literal or a list of filenames and a mapping of dependencies (use
    ``settings.CMSPLUGIN_CASCADE['dependencies']`` to check for details), return a list of other
    files resolving the dependency. The returned list is ordered, so that files having no further
    dependency come as first element and the passed in filenames come as the last element.
    Use this function to automatically resolve dependencies of CSS and JavaScript files in the
    ``Media`` subclasses.
    """
    from cmsplugin_cascade import settings

    warnings.warn(
        'resolve_dependencies() is deprecated and will be removed.',
        DeprecationWarning,
        stacklevel=2,
    )

    def find_file(path):
        for finder in get_finders():
            result = finder.find(path)
            if result:
                return result

    dependencies = []
    if isinstance(filenames, (list, tuple, set)):
        for filename in filenames:
            dependencies.extend(resolve_dependencies(filename))
    else:
        filename = filenames
        dependency_list = settings.CMSPLUGIN_CASCADE['dependencies'].get(filename)
        if dependency_list:
            dependencies.extend(resolve_dependencies(dependency_list))
        if find_file(filename):
            dependencies.append(filename)
    return remove_duplicates(dependencies)


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
