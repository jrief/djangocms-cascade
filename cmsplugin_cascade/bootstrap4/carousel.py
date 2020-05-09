import re
import logging
from django.forms import widgets
from django.forms.fields import IntegerField, MultipleChoiceField
from django.utils.safestring import mark_safe
from django.utils.translation import ngettext_lazy, gettext_lazy as _

from entangled.forms import EntangledModelFormMixin
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap4.fields import BootstrapMultiSizeField
from cmsplugin_cascade.bootstrap4.grid import Breakpoint
from cmsplugin_cascade.bootstrap4.picture import get_picture_elements
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap4.utils import IMAGE_RESIZE_OPTIONS
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.image import ImagePropertyMixin, ImageFormMixin

logger = logging.getLogger('cascade')


class CarouselSlidesFormMixin(ManageChildrenFormMixin, EntangledModelFormMixin):
    OPTION_CHOICES = [('slide', _("Animate")), ('pause', _("Pause")), ('wrap', _("Wrap"))]

    num_children = IntegerField(min_value=1, initial=1,
        label=_('Slides'),
        help_text=_('Number of slides for this carousel.'),
    )

    interval = IntegerField(
        label=_("Interval"),
        initial=5,
        help_text=_("Change slide after this number of seconds."),
    )

    options = MultipleChoiceField(
        label=_('Options'),
        choices=OPTION_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        initial=['slide', 'wrap', 'pause'],
        help_text=_("Adjust interval for the carousel."),
    )

    container_max_heights = BootstrapMultiSizeField(
        label=_("Carousel heights"),
        allowed_units=['px'],
        initial=['100px', '150px', '200px', '250px', '300px'],
        help_text=_("Heights of Carousel in pixels for distinct Bootstrap's breakpoints."),
    )

    resize_options = MultipleChoiceField(
        label=_("Resize Options"),
        choices=IMAGE_RESIZE_OPTIONS,
        widget=widgets.CheckboxSelectMultiple,
        help_text=_("Options to use when resizing the image."),
        initial=['upscale', 'crop', 'subject_location', 'high_resolution'],
    )

    class Meta:
        untangled_fields = ['num_children']
        entangled_fields = {'glossary': ['interval', 'options', 'container_max_heights', 'resize_options']}


class BootstrapCarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    default_css_class = 'carousel'
    default_css_attributes = ['options']
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cascade/bootstrap4/{}carousel.html'
    default_inline_styles = {'overflow': 'hidden'}
    form = CarouselSlidesFormMixin
    DEFAULT_CAROUSEL_ATTRIBUTES = {'data-ride': 'carousel'}

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_num_children()
        content = ngettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)
        return mark_safe(content)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapCarouselPlugin, cls).get_css_classes(obj)
        if 'slide' in obj.glossary.get('options', []):
            css_classes.append('slide')
        return css_classes

    @classmethod
    def get_html_tag_attributes(cls, obj):
        attributes = cls.super(BootstrapCarouselPlugin, cls).get_html_tag_attributes(obj)
        attributes.update(cls.DEFAULT_CAROUSEL_ATTRIBUTES)
        attributes['data-interval'] = 1000 * int(obj.glossary.get('interval', 5))
        options = obj.glossary.get('options', [])
        attributes['data-pause'] = 'pause' in options and 'hover' or 'false'
        attributes['data-wrap'] = 'wrap' in options and 'true' or 'false'
        return attributes

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, BootstrapCarouselSlidePlugin)
        obj.sanitize_children()

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super().sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        # fill all invalid heights for this container to a meaningful value
        max_height = max(obj.glossary['container_max_heights'].values())
        pattern = re.compile(r'^(\d+)px$')
        for bp in complete_glossary.get('breakpoints', ()):
            if not pattern.match(obj.glossary['container_max_heights'].get(bp, '')):
                obj.glossary['container_max_heights'][bp] = max_height
        return sanitized

plugin_pool.register_plugin(BootstrapCarouselPlugin)


class BootstrapCarouselSlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    model_mixins = (ImagePropertyMixin,)
    default_css_class = 'img-fluid'
    parent_classes = ['BootstrapCarouselPlugin']
    raw_id_fields = ['image_file']
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    render_template = 'cascade/bootstrap4/carousel-slide.html'
    form = ImageFormMixin
    alien_child_classes = True

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapCarouselSlidePlugin, self).render(context, instance, placeholder)
        # slide image shall be rendered in a responsive context using the ``<picture>`` element
        try:
            parent_glossary = instance.parent.get_bound_plugin().glossary
            instance.glossary.update(responsive_heights=parent_glossary['container_max_heights'])
            elements = get_picture_elements(instance)
        except Exception as exc:
            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            context.update({
                'is_fluid': False,
                'elements': elements,
            })
        return context

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super().sanitize_model(obj)
        resize_options = obj.get_parent_glossary().get('resize_options', [])
        if obj.glossary.get('resize_options') != resize_options:
            obj.glossary.update(resize_options=resize_options)
            sanitized = True
        parent = obj.parent
        while parent.plugin_type != 'BootstrapColumnPlugin':
            parent = parent.parent
            if parent is None:
                logger.warning("PicturePlugin(pk={}) has no ColumnPlugin as ancestor.".format(obj.pk))
                return
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
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Empty Slide")
        return mark_safe(content)

plugin_pool.register_plugin(BootstrapCarouselSlidePlugin)
