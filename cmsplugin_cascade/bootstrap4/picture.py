# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.forms import widgets, ModelChoiceField
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from filer.models.imagemodels import Image
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.image import ImageAnnotationMixin, ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from cmsplugin_cascade.utils import (compute_aspect_ratio, get_image_size, parse_responsive_length,
   compute_aspect_ratio_with_glossary, ramdon_color)

logger = logging.getLogger('cascade')


class BootstrapPicturePlugin(ImageAnnotationMixin, LinkPluginBase):
    name = _("Picture")
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = ('image_file',)
    admin_preview = False
    ring_plugin = 'PicturePlugin'
    render_template = 'cascade/bootstrap4/linked-picture.html'
    default_css_class = 'img-fluid'
    default_css_attributes = ('image_shapes',)
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    html_tag_attributes.update(LinkPluginBase.html_tag_attributes)
    fields = ['image_file'] + list(LinkPluginBase.fields)
    RESIZE_OPTIONS = [
        ('upscale', _("Upscale image")),
        ('crop', _("Crop image")),
        ('subject_location', _("With subject location")),
        ('high_resolution', _("Optimized for Retina"))
    ]

    responsive_heights = GlossaryField(
        MultipleCascadingSizeWidget([bp.name for bp in Breakpoint], allowed_units=['px', '%'], required=False),
        label=_("Adapt Picture Heights"),
        initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%', 'xl': '100%'},
        help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints."),
    )

    responsive_zoom = GlossaryField(
        MultipleCascadingSizeWidget([bp.name for bp in Breakpoint], allowed_units=['%'], required=False),
        label=_("Adapt Picture Zoom"),
        initial={'xs': '0%', 'sm': '0%', 'md': '0%', 'lg': '0%', 'xl': '0%'},
        help_text=_("Magnification of picture in percent for distinct Bootstrap's breakpoints."),
    )

    resize_options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
        label=_("Resize Options"),
        help_text=_("Options to use when resizing the image."),
        initial=['subject_location', 'high_resolution']
    )

    class Media:
        js = ['cascade/js/admin/pictureplugin.js']

    def get_form(self, request, obj=None, **kwargs):
        LINK_TYPE_CHOICES = [('none', _("No Link"))]
        LINK_TYPE_CHOICES.extend(t for t in getattr(LinkForm, 'LINK_TYPE_CHOICES') if t[0] != 'email')
        image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))
        Form = type(str('ImageForm'), (ImageFormMixin, getattr(LinkForm, 'get_form_class')(),),
                    {'LINK_TYPE_CHOICES': LINK_TYPE_CHOICES, 'image_file': image_file})
        kwargs.update(form=Form)
        return super(BootstrapPicturePlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the picture element
        try:
            elements = get_picture_elements(instance)
        except Exception as exc:
            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            context.update({
                'instance': instance,
                'is_fluid': True,
                'placeholder': placeholder,
                'elements': elements,
            })
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapPicturePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapPicturePlugin, cls).get_identifier(obj)
        try:
            content = force_text(obj.image)
        except AttributeError:
            content = _("No Picture")
        return format_html('{0}{1}', identifier, content)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = False
        parent = obj.parent
        if parent:
            while parent.plugin_type != 'BootstrapColumnPlugin':
                parent = parent.parent
            grid_column = parent.get_bound_plugin().get_grid_instance()
            obj.glossary.setdefault('media_queries', {})
            for bp in Breakpoint:
                obj.glossary['media_queries'].setdefault(bp.name, {})
                width = round(grid_column.get_bound(bp).max)
                if obj.glossary['media_queries'][bp.name].get('width') != width:
                    obj.glossary['media_queries'][bp.name]['width'] = width
                    sanitized = True
                if obj.glossary['media_queries'][bp.name].get('media') != bp.media_query:
                    obj.glossary['media_queries'][bp.name]['media'] = bp.media_query
                    sanitized = True
        else:
            logger.warning("PicturePlugin(pk={}) has no ColumnPlugin as ancestor.".format(obj.pk))
            return 
        return sanitized

plugin_pool.register_plugin(BootstrapPicturePlugin)


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
        instance.glossary['ramdom_svg_color'] = 'hsl({}, 30%, 80%, 0.8)'.format( str(random.randint(0, 360)))
    else:
        # if accessing the image file fails or fake image fails, abort here
        logger.warning("Unable to compute aspect ratio of image '{}'".format(instance.image))
        return

    container_max_heights = instance.glossary.get('container_max_heights', {})
    resize_options = instance.glossary.get('resize_options', {})
    crop = 'crop' in resize_options
    upscale = 'upscale' in resize_options
    if hasattr(instance.image, 'subject_location'):
        subject_location = instance.image.subject_location and 'subject_location' in resize_options
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
        elif bp in container_max_heights:
            container_height = parse_responsive_length(container_max_heights[bp])
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
        elem = {'tag': 'source', 'size': size, 'zoom': zoom, 'crop': crop,
                'upscale': upscale, 'subject_location': subject_location, 'media': media}
        if 'high_resolution' in resize_options:
            elem['size2'] = (size[0] * 2, size[1] * 2)
        elements.append(elem)

    # add a fallback image for old browsers which can't handle the <picture> element
    if image_height[1]:
        size = (int(max_width), int(round(max_width * aspect_ratio * image_height[1])))
    else:
        size = (int(max_width), int(round(max_width * aspect_ratio)))
    elements.append({'tag': 'img', 'size': size, 'zoom': max_zoom, 'crop': crop,
                     'upscale': upscale, 'subject_location': subject_location})
    return elements
