import logging
from django.forms import widgets, ChoiceField, MultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.bootstrap5.utils import get_image_tags, IMAGE_RESIZE_OPTIONS, IMAGE_SHAPE_CHOICES
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.fields import SizeField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin

logger = logging.getLogger('cascade.bootstrap5')


class BootstrapImageFormMixin(ImageFormMixin):
    image_shapes = MultipleChoiceField(
        label=_("Image Shapes"),
        choices=IMAGE_SHAPE_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        initial=['img-fluid']
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

    class Meta:
        entangled_fields = {'glossary': ['image_shapes', 'image_height', 'resize_options']}


class BootstrapImagePlugin(LinkPluginBase):
    name = _("Image <img>")
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = LinkPluginBase.raw_id_fields + ['image_file']
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    admin_preview = False
    ring_plugin = 'ImagePlugin'
    form = type('BootstrapImageForm', (LinkFormMixin, BootstrapImageFormMixin), {'require_link': False})
    render_template = 'cascade/bootstrap5/linked-image.html'
    default_css_attributes = ['image_shapes', 'image_alignment']
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    html_tag_attributes.update(LinkPluginBase.html_tag_attributes)

    class Media:
        js = ['cascade/admin/bootstrap5/js/imageplugin.js']

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
            content = gettext("No Image")
        return mark_safe(content)

plugin_pool.register_plugin(BootstrapImagePlugin)
