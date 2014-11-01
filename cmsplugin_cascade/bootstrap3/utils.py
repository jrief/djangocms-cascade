# -*- coding: utf-8 -*-
from django.forms import widgets
from cmsplugin_cascade.plugin_base import CascadePluginBase


def reduce_breakpoints(plugin, field_name):
    """
    Narrow down the number of breakpoints in the widget of the named glossary_field. This is useful
    in case the container was defined with a subset of these breakpoints: xs, sm, md, lg.
    """
    if not isinstance(plugin, CascadePluginBase):
        raise ValueError('Plugin is not of type CascadePluginBase')
    complete_glossary = plugin.get_parent_instance().get_complete_glossary()
    if 'breakpoints' not in complete_glossary:
        return
    # find the glossary_field named 'responsive-heights' and restrict its breakpoint to the available ones
    widget = [f for f in plugin.glossary_fields if f.name == field_name][0].widget
    if not isinstance(widget, widgets.MultiWidget):
        raise ValueError('Widget for glossary_field {0} does not a multiple values')
    temp = [(l, widget.widgets[k]) for k, l in enumerate(widget.labels) if l in complete_glossary['breakpoints']]
    widget.labels, widget.widgets = (list(t) for t in zip(*temp))


def get_responsive_appearances(context, instance):
    """
    Create the appearance context, used to render a <picture> element which automatically adopts
    its sizes to the current column width.
    """
    complete_glossary = instance.get_complete_glossary()
    if instance.image.exif.get('Orientation', 1) > 4:
        # image is rotated by 90 degrees, while keeping width and height
        aspect_ratio = float(instance.image.width) / float(instance.image.height)
    else:
        aspect_ratio = float(instance.image.height) / float(instance.image.width)
    container_max_heights = complete_glossary.get('container_max_heights', {})
    resize_options = instance.glossary.get('resize-options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    subject_location = 'subject_location' in resize_options
    min_width = 100.0
    appearances = {}
    resolutions = (False, True) if 'high_resolution' in resize_options else (False,)
    image_height = (None, None)
    for high_res in resolutions:
        for bp in complete_glossary['breakpoints']:
            try:
                width = float(complete_glossary['container_max_widths'][bp])
            except KeyError:
                width = 0
            min_width = min(min_width, round(width))
            size = None
            try:
                image_height = _parse_responsive_height(instance.glossary['responsive-heights'][bp])
            except KeyError:
                pass
            if image_height[0]:
                size = (int(width), image_height[0])
            elif image_height[1]:
                size = (int(width), int(round(width * aspect_ratio * image_height[1])))
            elif bp in container_max_heights:
                container_height = _parse_responsive_height(container_max_heights[bp])
                if container_height[0]:
                    size = (int(width), container_height[0])
                elif container_height[1]:
                    size = (int(width), int(round(width * aspect_ratio * container_height[1])))
            if size is None:
                # as fallback, adopt height to current width
                size = (int(width), int(round(width * aspect_ratio)))
            media_queries = complete_glossary['media_queries'][bp][:]
            if high_res:
                size = (size[0] * 2, size[1] * 2)
                media_queries.append('(min-resolution: 1.5dppx)')
            elif True in resolutions:
                media_queries.append('(max-resolution: 1.5dppx)')
            key = high_res and bp + '-retina' or bp
            media = ' and '.join(media_queries)
            appearances[key] = {'size': size, 'crop': crop, 'upscale': upscale,
                                'subject_location': subject_location, 'media': media}
    # create a relatively small image for the default img tag.
    if image_height[1]:
        size = (int(min_width), int(round(min_width * aspect_ratio * image_height[1])))
    else:
        size = (int(min_width), int(round(min_width * aspect_ratio)))
    default_appearance = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
    return appearances, default_appearance


def get_static_appearance(context, instance):
    size = instance.glossary.get('image-size', {})
    resize_options = instance.glossary.get('resize-options', {})
    width = int(size.get('width', '').strip().rstrip('px') or 0)
    height = int(size.get('height', '').strip().rstrip('px') or 0)
    if width == 0 and height == 0:
        # use the original image's dimensions
        width = instance.image.width
        height = instance.image.height
    size = (width, height)
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    subject_location = 'subject_location' in resize_options
    appearance = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
    return appearance


def _parse_responsive_height(responsive_height):
    """
    Takes a string containing the image height in pixels or percent and parses it to obtain
    a computational height. It return a tuple with the height in pixels and its relative height,
    where depending on the input value, one or both elements are None.
    """
    responsive_height = responsive_height.strip()
    if responsive_height.endswith('px'):
        return (int(responsive_height.rstrip('px')), None)
    elif responsive_height.endswith('%'):
        return (None, float(responsive_height.rstrip('%')) / 100)
    return (None, None)
