# -*- coding: utf-8 -*-
import six
from django.forms import widgets
from django.forms import fields
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.image.models import ImageElement
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase
from cmsplugin_cascade.widgets import CascadingSizeWidget, MultipleCascadingSizeWidget
from .settings import CASCADE_BREAKPOINTS_DICT


class PictureForm(LinkForm):
    TYPE_CHOICES = (('null', _("No Link")), ('int', _("Internal")), ('ext', _("External")),)
    link_type = fields.ChoiceField(choices=TYPE_CHOICES, initial='null')

    class Meta:
        model = ImageElement
        fields = ('page_link', 'image', 'glossary',)


class BootstrapPicturePlugin(LinkPluginBase):
    name = _("Picture")
    model = ImageElement
    form = PictureForm
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'CarouselSlidePlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = ('image',)
    text_enabled = True
    admin_preview = False
    render_template = 'cms/bootstrap3/picture.html'
    default_css_attributes = ('image-shapes',)
    glossary_attributes = {'image-title': 'title', 'alt-tag': 'tag'}
    fields = ('image', 'glossary', ('link_type', 'page_link', 'url', 'email'),)
    SHAPE_CHOICES = (('img-responsive', _("Responsive")), ('img-rounded', _('Rounded')),
                     ('img-circle', _('Circle')), ('img-thumbnail', _('Thumbnail')),)
    RESIZE_OPTIONS = (('upscale', _("Upscale image")), ('crop', _("Crop image")),
                      ('subject_location', _("With subject location")),)
    APPEARANCE = {
        'xs': {'media': '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['sm'][0])},
        'sm': {'media': '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['md'][0])},
        'md': {'media': '(max-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['lg'][0])},
        'lg': {'media': '(min-width: {0}px)'.format(CASCADE_BREAKPOINTS_DICT['lg'][0])},
    }
    glossary_fields = (
        PartialFormField('image-title',
            widgets.TextInput(),
            label=_('Image Title'),
            help_text=_("Caption text added to the 'title' attribute of the <img> element."),
        ),
        PartialFormField('alt-tag',
            widgets.TextInput(),
            label=_('Alternative Description'),
            help_text=_("Textual description of the image added to the 'alt' tag of the <img> element."),
        ),
        PartialFormField('image-shapes',
            widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
            label=_("Image Shapes"),
            initial=['img-responsive']
        ),
        PartialFormField('responsive-height',
            CascadingSizeWidget(allowed_units=['px', '%'], required=False),
            label=_("Override Container Height"),
            help_text=_("An optional image height in '%' (percent) or 'px' (pixels) to override the container's size."),
        ),
        PartialFormField('image-size',
            MultipleCascadingSizeWidget(['width', 'height'], allowed_units=['px'], required=False),
            label=_("Image Size"),
            help_text=_("Specify image width and height in 'px' (pixels)."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['subject_location']
        ),
    )

    def render(self, context, instance, placeholder):
        if 'img-responsive' in instance.glossary.get('image-shapes', []):
            # image shall be rendered in a responsive context using the picture element
            appearances, default_appearance = self._responsive_appearances(context, instance)
            context.update({
                'is_responsive': True,
                'instance': instance,
                'placeholder': placeholder,
                'appearances': appearances,
                'default_appearance': default_appearance,
            })
        else:
            # image shall be rendered using fixed sizes
            appearance = self._static_appearance(context, instance)
            context.update({
                'is_responsive': False,
                'instance': instance,
                'placeholder': placeholder,
                'appearance': appearance,
            })
        return context

    def _responsive_appearances(self, context, instance):
        """
        Create the appearance context, used to render a <picture> element which automatically adopts
        its sizes to the current column width.
        """
        complete_glossary = instance.get_complete_glossary()
        aspect_ratio = float(instance.image.height) / float(instance.image.width)
        image_height = self._parse_image_height(instance.glossary['responsive-height'])
        container_max_heights = complete_glossary.get('container_max_heights', {})
        resize_options = instance.glossary.get('resize-options', {})
        crop = 'crop' in resize_options
        upscale = 'upscale' in resize_options
        subject_location = 'subject_location' in resize_options
        min_width = 100.0
        appearances = {}
        for bp in complete_glossary['breakpoints']:
            width = float(complete_glossary['container_max_widths'][bp])
            min_width = min(min_width, round(width))
            size = None
            if image_height[0]:
                size = (int(width), image_height[0])
            elif image_height[1]:
                size = (int(width), int(round(width * aspect_ratio * image_height[1])))
            elif bp in container_max_heights:
                container_height = self._parse_image_height(container_max_heights[bp])
                if container_height[0]:
                    size = (int(width), container_height[0])
                elif container_height[1]:
                    size = (int(width), int(round(width * aspect_ratio * container_height[1])))
            if size is None:
                # as fallback, adopt height to current width
                size = (int(width), int(round(width * aspect_ratio)))
            appearances[bp] = self.APPEARANCE[bp].copy()
            appearances[bp].update(size=size, crop=crop, upscale=upscale, subject_location=subject_location)
        # create a relatively small image for the default img tag.
        if image_height[1]:
            size = (int(min_width), int(round(min_width * aspect_ratio * image_height[1])))
        else:
            size = (int(min_width), int(round(min_width * aspect_ratio)))
        default_appearance = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
        return appearances, default_appearance

    def _static_appearance(self, context, instance):
        size = instance.glossary.get('image-size', {})
        width = int(size.get('width', '').strip().rstrip('px') or 0)
        height = int(size.get('height', '').strip().rstrip('px') or 0)
        if width == 0 and height == 0:
            # use the original image's dimensions
            width = instance.image.width
            height = instance.image.height
        size = (width, height)
        resize_options = instance.glossary.get('resize-options', {})
        crop = 'crop' in resize_options
        upscale = 'upscale' in resize_options
        subject_location = 'subject_location' in resize_options
        appearance = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
        return appearance

    @staticmethod
    def _parse_image_height(image_height):
        """
        Takes a string containing the image height in pixels or percent and parses it to obtain
        a computational height. It return a tuple with the height in pixels and its relative height,
        where depending on the input value, one or both elements are None.
        """
        image_height = image_height.strip()
        if image_height.endswith('px'):
            return (int(image_height.rstrip('px')), None)
        elif image_height.endswith('%'):
            return (None, float(image_height.rstrip('%')) / 100)
        return (None, None)

    @classmethod
    def get_identifier(cls, obj):
        return six.u(str(obj.image))

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapPicturePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def x_sanitize_model(cls, obj):
        """
        By using the full glossary context this image will be rendered into, estimate the maximum
        image size. Remember: In Bootstrap 3, images usually are rendered into a column, whose width
        is responsive, thus the image size shall be no more than its maximum size.
        """
        sanitized = super(BootstrapPicturePlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        breakpoints = ('xs', 'sm', 'md', 'lg')
        container_bp = complete_glossary.get('breakpoint', 'lg')
        breakpoints = breakpoints[:breakpoints.index(container_bp) + 1]
        estimated_max_width = obj.glossary.get('estimated_max_width')
        max_width = 0
        column_width = None
        for bp in breakpoints:
            # find out the width in column units, if missing use a smaller width
            width = complete_glossary.get('{0}-column-width'.format(bp), '').replace('col-{0}-'.format(bp), '')
            if width.isdigit():
                column_width = width
            elif column_width is None:
                column_width = 12
            # estimate the largest width in pixels this image ever might be rendered
            width = settings.CMS_CASCADE_BOOTSTRAP3_COLUMN_WIDTHS[bp] * int(column_width)
            max_width = max(max_width, int(round(width)))
        obj.glossary.update(estimated_max_width=max_width)
        return sanitized or estimated_max_width != max_width

plugin_pool.register_plugin(BootstrapPicturePlugin)
