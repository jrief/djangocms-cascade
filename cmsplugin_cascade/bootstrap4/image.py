import logging
from django.forms import widgets, ChoiceField, MultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.bootstrap4.utils import get_image_tags, IMAGE_RESIZE_OPTIONS, IMAGE_SHAPE_CHOICES
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.fields import SizeField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin

logger = logging.getLogger('cascade.bootstrap4')


class BootstrapImageFormMixin(ImageFormMixin):
    ALIGNMENT_OPTIONS = [
        ('float-left', _("Left")),
        ('float-right', _("Right")),
        ('mx-auto', _("Center")),
    ]

    image_shapes = MultipleChoiceField(
        label=_("Image Shapes"),
        choices=IMAGE_SHAPE_CHOICES,
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
        choices=IMAGE_RESIZE_OPTIONS,
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
