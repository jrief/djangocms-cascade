# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from collections import OrderedDict
from django.conf import settings
from django.forms import widgets
from cmsplugin_cascade.plugin_base import CascadePluginBase

__all__ = ['reduce_breakpoints', 'compute_media_queries', 'get_image_tags', 'get_picture_elements',
           'get_widget_choices']

logger = logging.getLogger('cascade')

BS3_BREAKPOINTS = OrderedDict(settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])
BS3_BREAKPOINT_KEYS = list(tp[0] for tp in settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])


def get_widget_choices():
    breakpoints = list(BS3_BREAKPOINTS)
    i = 0
    widget_choices = []
    for br, br_options in BS3_BREAKPOINTS.items():
        if i == 0:
            widget_choices.append((br, '{} (<{}px)'.format(br_options[2], br_options[0])))
        elif i == len(breakpoints[:-1]):
            widget_choices.append((br, '{} (≥{}px)'.format(br_options[2], br_options[0])))
        else:
            widget_choices.append((br, '{} (≥{}px and <{}px)'.format(br_options[2], br_options[0], BS3_BREAKPOINTS[breakpoints[(i + 1)]][0])))
        i += 1
    return widget_choices


def reduce_breakpoints(plugin, field_name, request=None):
    """
    Narrow down the number of breakpoints in the widget of the named glossary_field. This is useful
    in case the container was defined with a subset of these breakpoints: xs, sm, md, lg.
    """
    if not isinstance(plugin, CascadePluginBase):
        raise ValueError('Plugin is not of type CascadePluginBase')
    parent_instance = plugin.get_parent_instance(request)
    if not parent_instance:
        return
    complete_glossary = parent_instance.get_complete_glossary()
    if 'breakpoints' not in complete_glossary:
        return
    try:
        # find the glossary_field named field_name and restrict its breakpoint to the available ones
        widget = [f for f in plugin.glossary_fields if f.name == field_name][0].widget
    except IndexError:
        return
    if not isinstance(widget, widgets.MultiWidget):
        raise ValueError('Widget for glossary_field {0} is not a multiple value field')
    temp = [(l, widget.widgets[k]) for k, l in enumerate(widget.labels) if l in complete_glossary['breakpoints']]
    widget.labels, widget.widgets = (list(t) for t in zip(*temp))


def compute_media_queries(element):
    """
    For e given Cascade element, compute the current media queries for each breakpoint,
    even for nested containers, rows and columns.
    """
    parent_glossary = element.get_parent_glossary()
    # compute the max width and the required media queries for each chosen breakpoint
    element.glossary['container_max_widths'] = max_widths = {}
    element.glossary['media_queries'] = media_queries = {}
    breakpoints = element.glossary.get('breakpoints', parent_glossary.get('breakpoints', []))
    last_index = len(breakpoints) - 1
    fluid = element.glossary.get('fluid')
    for index, bp in enumerate(breakpoints):
        try:
            key = 'container_fluid_max_widths' if fluid else 'container_max_widths'
            max_widths[bp] = parent_glossary[key][bp]
        except KeyError:
            max_widths[bp] = BS3_BREAKPOINTS[bp][4 if fluid else 3]
        if last_index > 0:
            if index == 0:
                next_bp = breakpoints[1]
                media_queries[bp] = ['(max-width: {0}px)'.format(BS3_BREAKPOINTS[next_bp][0])]
            elif index == last_index:
                media_queries[bp] = ['(min-width: {0}px)'.format(BS3_BREAKPOINTS[bp][0])]
            else:
                next_bp = breakpoints[index + 1]
                media_queries[bp] = ['(min-width: {0}px)'.format(BS3_BREAKPOINTS[bp][0]),
                                     '(max-width: {0}px)'.format(BS3_BREAKPOINTS[next_bp][0])]


def compute_aspect_ratio(image):
    if image.exif.get('Orientation', 1) > 4:
        # image is rotated by 90 degrees, while keeping width and height
        return float(image.width) / float(image.height)
    else:
        return float(image.height) / float(image.width)


def get_image_tags(context, instance, options):
    """
    Create a context returning the tags to render an <img ...> element:
    ``sizes``, ``srcset``, a fallback ``src`` and if required inline styles.
    """
    try:
        aspect_ratio = compute_aspect_ratio(instance.image)
    except Exception as e:
        # if accessing the image file fails, abort here
        return
    is_responsive = options.get('is_responsive', False)
    resize_options = options.get('resize_options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    subject_location = instance.image.subject_location if 'subject_location' in resize_options else False
    resolutions = (False, True) if 'high_resolution' in resize_options else (False,)
    tags = {'sizes': [], 'srcsets': {}, 'is_responsive': is_responsive, 'extra_styles': {}}
    if is_responsive:
        image_width = _parse_responsive_length(options.get('image_width_responsive') or '100%')
        assert(image_width[1]), "The given image has no valid width"
        if image_width[1] != 1.0:
            tags['extra_styles'].update({'max-width': '{:.0f}%'.format(100 * image_width[1])})
    else:
        image_width = _parse_responsive_length(options['image_width_fixed'])
        if not image_width[0]:
            image_width = (instance.image.width, image_width[1])
    try:
        image_height = _parse_responsive_length(options['image_height'])
    except KeyError:
        image_height = (None, None)
    set_defaults(options)
    if is_responsive:
        max_width = 0
        for bp in options['breakpoints']:
            if bp not in options['container_max_widths']:
                continue
            width = int(image_width[1] * options['container_max_widths'][bp])
            max_width = max(max_width, width)
            size = _get_image_size(width, image_height, aspect_ratio)
            if bp in options['media_queries']:
                tags['sizes'].append('{0} {1}px'.format(' and '.join(options['media_queries'][bp]), width))
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
        size = _get_image_size(image_width[0], image_height, aspect_ratio)
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


def set_defaults(options):
    options.setdefault('breakpoints', ['xs', 'sm', 'md', 'lg'])
    options.setdefault('container_max_widths', {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170})
    options.setdefault('fluid', False)
    options.setdefault('media_queries', {
        'xs': ['(max-width: 768px)'],
        'sm': ['(min-width: 768px)', '(max-width: 992px)'],
        'md': ['(min-width: 992px)', '(max-width: 1200px)'],
        'lg': ['(min-width: 1200px)'],
    })


def get_picture_elements(context, instance):
    """
    Create a context, used to render a <picture> together with all its ``<source>`` elements:
    It returns a list of HTML elements, each containing the information to render a ``<source>``
    element.
    The purpose of this HTML entity is to display images with art directions. For normal images use
    the ``<img>`` element.
    """
    if not instance.image:
        return
    complete_glossary = instance.get_complete_glossary()
    aspect_ratio = compute_aspect_ratio(instance.image)
    container_max_heights = complete_glossary.get('container_max_heights', {})
    resize_options = instance.glossary.get('resize_options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    subject_location = instance.image.subject_location if 'subject_location' in resize_options else False
    max_width = 0
    max_zoom = 0
    elements = []
    resolutions = (False, True) if 'high_resolution' in resize_options else (False,)
    for high_res in resolutions:
        for bp in complete_glossary['breakpoints']:
            try:
                width = float(complete_glossary['container_max_widths'][bp])
            except KeyError:
                width = 0
            max_width = max(max_width, round(width))
            size = None
            try:
                image_height = _parse_responsive_length(instance.glossary['responsive_heights'][bp])
            except KeyError:
                image_height = (None, None)
            if image_height[0]:  # height was given in px
                size = (int(width), image_height[0])
            elif image_height[1]:  # height was given in %
                size = (int(width), int(round(width * aspect_ratio * image_height[1])))
            elif bp in container_max_heights:
                container_height = _parse_responsive_length(container_max_heights[bp])
                if container_height[0]:
                    size = (int(width), container_height[0])
                elif container_height[1]:
                    size = (int(width), int(round(width * aspect_ratio * container_height[1])))
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
            try:
                media_queries = complete_glossary['media_queries'][bp][:]
            except KeyError:
                media_queries = []
            if high_res:
                size = (size[0] * 2, size[1] * 2)
                media_queries.append('(min-resolution: 1.5dppx)')
            elif True in resolutions:
                media_queries.append('(max-resolution: 1.5dppx)')
            media = ' and '.join(media_queries)
            elements.append({'tag': 'source', 'size': size, 'zoom': zoom, 'crop': crop,
                    'upscale': upscale, 'subject_location': subject_location, 'media': media})
    if image_height[1]:
        size = (int(max_width), int(round(max_width * aspect_ratio * image_height[1])))
    else:
        size = (int(max_width), int(round(max_width * aspect_ratio)))
    elements.append({'tag': 'img', 'size': size, 'zoom': max_zoom, 'crop': crop, 'upscale': upscale,
                     'subject_location': subject_location})
    return elements


def _get_image_size(width, image_height, aspect_ratio):
    if image_height[0]:
        # height was given in px
        return (width, image_height[0])
    elif image_height[1]:
        # height was given in %
        return (width, int(round(width * image_height[1])))
    else:
        # as fallback, adopt height to current width
        return (width, int(round(width * aspect_ratio)))


def _parse_responsive_length(responsive_length):
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
