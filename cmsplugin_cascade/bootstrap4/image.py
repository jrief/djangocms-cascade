import logging
from django.forms import widgets, ChoiceField, MultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.fields import SizeField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.utils import (compute_aspect_ratio, get_image_size, parse_responsive_length,
   compute_aspect_ratio_with_glossary)

logger = logging.getLogger('cascade')


class BootstrapImageFormMixin(ImageFormMixin):
    SHAPE_CHOICES = [
        ('img-fluid', _("Responsive")),
        ('rounded', _('Rounded')),
        ('rounded-circle', _('Circle')),
        ('img-thumbnail', _('Thumbnail')),
    ]

    RESIZE_OPTIONS = [
        ('upscale', _("Upscale image")),
        ('crop', _("Crop image")),
        ('subject_location', _("With subject location")),
        ('high_resolution', _("Optimized for Retina")),
    ]

    ALIGNMENT_OPTIONS = [
        ('float-left', _("Left")),
        ('float-right', _("Right")),
        ('mx-auto', _("Center")),
    ]

    image_shapes = MultipleChoiceField(
        label=_("Image Shapes"),
        choices=SHAPE_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        initial=['img-fluid']
    )

    image_width_responsive = SizeField(
        label=_("Responsive Image Width"),
        allowed_units=['%'],
        initial='100%',
        required = False,
        help_text=_("Set the image width in percent relative to containing element."),
    )

    image_width_fixed = SizeField(
        label=_("Fixed Image Width"),
        allowed_units=['px'],
        required = False,
        help_text=_("Set a fixed image width in pixels."),
    )

    image_height = SizeField(
        label=_("Adapt Image Height"),
        allowed_units=['px', '%'],
        required = False,
        help_text=_("Set a fixed height in pixels, or percent relative to the image width."),
    )

    resize_options = MultipleChoiceField(
        label=_("Resize Options"),
        choices=RESIZE_OPTIONS,
        widget=widgets.CheckboxSelectMultiple,
        required = False,
        help_text=_("Options to use when resizing the image."),
        initial=['subject_location', 'high_resolution'],
    )

    image_alignment = ChoiceField(
        label=_("Image Alignment"),
        choices=ALIGNMENT_OPTIONS,
        widget=widgets.RadioSelect,
        required = False,
        help_text=_("How to align a non-responsive image."),
    )

    class Meta:
        entangled_fields = {'glossary': ['image_shapes', 'image_width_responsive', 'image_width_fixed',
                                         'image_height', 'resize_options', 'image_alignment']}


class BootstrapImagePlugin(LinkPluginBase):
    name = _("Image")
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = LinkPluginBase.raw_id_fields + ['image_file']
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    admin_preview = False
    ring_plugin = 'ImagePlugin'
    form = type('BootstrapImageForm', (LinkFormMixin, BootstrapImageFormMixin), {'require_link': False})
    render_template = 'cascade/bootstrap4/linked-image.html'
    default_css_attributes = ['image_shapes', 'image_alignment']
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    html_tag_attributes.update(LinkPluginBase.html_tag_attributes)

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/imageplugin.js']

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapImagePlugin, self).render(context, instance, placeholder)
        try:
            image_tags = get_image_tags(instance)
        except Exception as exc:
            logger.warning("Unable generate image tags. Reason: {}".format(exc))
        else:
            extra_styles = image_tags.pop('extra_styles', None)
            if extra_styles:
                inline_styles = instance.glossary.get('inline_styles', {})
                inline_styles.update(extra_styles)
                instance.glossary['inline_styles'] = inline_styles
            context.update(dict(**image_tags))
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapImagePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        try:
            content = str(obj.image)
        except AttributeError:
            content = _("No Image")
        return mark_safe(content)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = False
        parent = obj.parent
        try:
            while parent.plugin_type != 'BootstrapColumnPlugin':
                parent = parent.parent
            grid_column = parent.get_bound_plugin().get_grid_instance()
            min_max_bounds = grid_column.get_min_max_bounds()
            if obj.glossary.get('column_bounds') != min_max_bounds:
                obj.glossary['column_bounds'] = min_max_bounds
                sanitized = True
            obj.glossary.setdefault('media_queries', {})
            for bp in Breakpoint:
                media_query = '{} {:.2f}px'.format(bp.media_query, grid_column.get_bound(bp).max)
                if obj.glossary['media_queries'].get(bp.name) != media_query:
                    obj.glossary['media_queries'][bp.name] = media_query
                    sanitized = True
        except AttributeError:
            logger.warning("ImagePlugin(pk={}) has no ColumnPlugin as ancestor.".format(obj.pk))
            return
        return sanitized

plugin_pool.register_plugin(BootstrapImagePlugin)


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
