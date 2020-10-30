import logging
from django.forms import widgets, MultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.bootstrap4.utils import get_picture_elements, IMAGE_RESIZE_OPTIONS, IMAGE_SHAPE_CHOICES
from cmsplugin_cascade.bootstrap4.fields import BootstrapMultiSizeField
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin

logger = logging.getLogger('cascade.bootstrap4')


class BootstrapPictureFormMixin(ImageFormMixin):
    responsive_heights = BootstrapMultiSizeField(
        label=_("Adapt Picture Heights"),
        required=False,
        require_all_fields=False,
        allowed_units=['px', '%'],
        initial='100%',
        help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints."),
    )

    responsive_zoom = BootstrapMultiSizeField(
        label=_("Adapt Picture Zoom"),
        required=False,
        require_all_fields=False,
        allowed_units=['%'],
        initial=['0%', '0%', '0%', '0%', '0%'],
        help_text=_("Magnification of picture in percent for distinct Bootstrap's breakpoints."),
    )

    resize_options = MultipleChoiceField(
        label=_("Resize Options"),
        choices=IMAGE_RESIZE_OPTIONS,
        widget=widgets.CheckboxSelectMultiple,
        initial=['subject_location', 'high_resolution'],
        help_text = _("Options to use when resizing the image."),
    )

    image_shapes = MultipleChoiceField(
        label=_("Image Shapes"),
        choices=IMAGE_SHAPE_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        initial=['img-fluid']
    )

    class Meta:
        entangled_fields = {'glossary': ['responsive_heights', 'responsive_zoom', 'resize_options', 'image_shapes']}


class BootstrapPicturePlugin(LinkPluginBase):
    name = _("Picture")
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = LinkPluginBase.raw_id_fields + ['image_file']
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    admin_preview = False
    ring_plugin = 'PicturePlugin'
    form = type('BootstrapPictureForm', (LinkFormMixin, BootstrapPictureFormMixin), {'require_link': False})
    render_template = 'cascade/bootstrap4/linked-picture.html'
    default_css_class = 'img-fluid'
    default_css_attributes = ['image_shapes']
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    html_tag_attributes.update(LinkPluginBase.html_tag_attributes)

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/pictureplugin.js']

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the picture element
        context = self.super(BootstrapPicturePlugin, self).render(context, instance, placeholder)
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
        try:
            content = str(obj.image)
        except AttributeError:
            content = _("No Picture")
        return mark_safe(content)

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
