import logging
from math import sqrt

from django.core.files.storage import default_storage
from django.forms import fields, widgets, MultipleChoiceField
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _

from cms.models.pluginmodel import CMSPlugin
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from finder.models.file import FileModel as FinderFileModel

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.bootstrap5.hyperlink import HyperlinkForm, HyperlinkPluginMixin, LinkTypeChoiceField
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.utils import IMAGE_SHAPE_CHOICES
from finder.forms.fields import FinderFileField

logger = logging.getLogger('cascade.bootstrap5')


class AspectRatioChoiceField(fields.ChoiceField):
    def __init__(self, breakpoint, *args, **kwargs):
        kwargs.setdefault('label', gettext("Aspect Ratio for ‘{}’").format(breakpoint.label))
        choices = [
            ('orig', _("Original")),
            ('16/9', "16:9"),
            ('4/3', "4:3"),
            ('1/1', "1:1"),
            ('2/1', "2:1"),
            ('21/9', "21:9"),
            ('3/2', "3:2"),
            ('2/3', "2:3"),
            ('3/4', "3:4"),
            ('9/16', "9:16"),
            ('9/21', "9:21"),
            ('1/2', "1:2"),
        ]
        if empty_label := kwargs.pop('empty_label', None):
            choices.insert(
                0,
                ('', empty_label)
            )
        kwargs.setdefault('choices', choices)
        super().__init__(*args, **kwargs)


class BootstrapPictureForm(HyperlinkForm):
    image = FinderFileField(
        accept_mime_types=['image/*'],
        label=_("Image"),
    )
    aspect_ratio = AspectRatioChoiceField(Breakpoint.xs)
    image_shapes = MultipleChoiceField(
        label=_("Image Shapes"),
        choices=IMAGE_SHAPE_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
    )
    link_type = LinkTypeChoiceField(required=False)

    class Meta(HyperlinkForm.Meta):
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['image', 'aspect_ratio', 'image_shapes'] + HyperlinkForm.Meta.fields_map['glossary']}


class ImageElementMixin:
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering an image element.
    """
    def __str__(self):
        try:
            return self.plugin_class.get_identifier(self)
        except AttributeError:
            return str(self.image)

    @property
    def image(self):
        if not hasattr(self, '_image_file'):
            if file_uuid := self.glossary.get('image'):
                self._image_instance = FinderFileModel.objects.get_inode(id=file_uuid, is_folder=False)
            else:
                self._image_instance = None
        return self._image_instance


class BootstrapPicturePlugin(HyperlinkPluginMixin, BootstrapPluginBase):
    name = _("Picture")
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    allow_children = False
    model_mixins = (LinkElementMixin, ImageElementMixin)
    admin_preview = False
    form = BootstrapPictureForm
    render_template = 'cascade/bootstrap5/picture.html'
    default_css_attributes = ['image_shapes']
    default_css_class = 'lazyload text-bg-light img-fluid w-100'
    step_size_bytes = 25 * 1024  # thumbnail images in steps of 25kB
    min_thumbnail_width = 306
    max_thumbnail_width = 1920
    max_pixel_ratio = 2.0  # maximum pixel ratio for the image
    real_to_wanted_ratio = (0.9, 1.1)  # acceptable ratio between wanted and real thumbnail size
    fallback_image = static('cascade/fallback.svg')
    # html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    # html_tag_attributes.update(LinkPluginBase.html_tag_attributes)

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
            content = gettext("No Picture")
        return mark_safe(content)

    def get_model_form(self):
        if self.object:
            breakpoints = self.get_breakpoints(self.object)
        elif 'plugin_parent' in self.request.GET:
            breakpoints = self.get_breakpoints(CMSPlugin.objects.get(pk=self.request.GET['plugin_parent']))
        else:
            breakpoints = []
        if 'xs' in breakpoints:
            breakpoints.remove('xs')

        model_form = super().get_model_form()
        glossary_fields = list(model_form.Meta.fields_map['glossary'])
        attrs, prev_bp = {}, 'xs'
        for index, bp in enumerate(breakpoints, glossary_fields.index('aspect_ratio') + 1):
            if bp == 'xs':
                continue
            field_name = f'aspect_ratio_{bp}'
            attrs[field_name] = AspectRatioChoiceField(
                Breakpoint[bp],
                required=False,
                empty_label=_("Inherit from “Aspect Ratio for ‘{}’”").format(Breakpoint[prev_bp].label),
            )
            glossary_fields.insert(index, field_name)

        attrs['Meta'] = type('Meta', (model_form.Meta,), {
            'fields_map': {'glossary': glossary_fields},
        })
        model_form = type(model_form.__name__, model_form.__mro__, attrs)
        return model_form

    def get_picture_sources(self, instance):
        allowed_breakpoints = self.get_breakpoints(instance)
        sources = []
        source_element = prev_aspect_ratio = None
        for breakpoint in Breakpoint:
            if breakpoint == Breakpoint.xs:
                aspect_ratio = instance.glossary['aspect_ratio']
            elif breakpoint.name in allowed_breakpoints:
                aspect_ratio = instance.glossary.get(f'aspect_ratio_{breakpoint.name}')

            if aspect_ratio == 'orig':
                computed_aspect_ratio = instance.image.width / instance.image.height
            elif aspect_ratio :
                computed_aspect_ratio = float(eval(aspect_ratio))
            else:
                aspect_ratio = prev_aspect_ratio

            if aspect_ratio != prev_aspect_ratio:
                width = min(self.min_thumbnail_width, instance.image.width)
                height = min(width / computed_aspect_ratio, instance.image.height)
                source_element = {
                    'aspect_ratio': computed_aspect_ratio,
                    'min_width': f"{breakpoint.min_width}px" if breakpoint.min_width else None,
                    'lower_bound': {'width': width, 'height': height},
                }
                sources.append(source_element)

            source_element['max_width'] = f"{breakpoint.max_width - 0.02}px" if breakpoint.max_width else None
            width = breakpoint.max_width if breakpoint.max_width else self.max_thumbnail_width
            width = min(width * self.max_pixel_ratio, instance.image.width)
            height = min(width / computed_aspect_ratio, instance.image.height)
            source_element['upper_bound'] = {'width': width, 'height': height}
            prev_aspect_ratio = aspect_ratio

        return sources

    def get_or_create_thumbnail(self, image, width, height):
        width, height = min(round(width), image.width), min(round(height), image.height)
        thumbnail_path = image.get_thumbnail_path(width, height)
        if default_storage.exists(thumbnail_path):
            return thumbnail_path
        try:
            image.crop(thumbnail_path, width, height)
        except Exception as exc:
            logger.warning("Unable generate picture context. Reason: {}".format(exc))
        return thumbnail_path

    def render(self, context, instance, placeholder):
        """
        Create a context, used to render a <picture> together with all its ``<source>`` elements:
        It returns a list of HTML elements, each containing the information to render a ``<source>``
        element.
        The purpose of this HTML entity is to display images with art directions. For normal images use
        the ``<img>`` element.
        """

        def estimate_compression_factor(thumb_w, thumb_h, thumb_size):
            pixel_ratio = round(thumb_w) * round(thumb_h) / upper_image_area
            return upper_image_size * pixel_ratio / thumb_size

        # image shall be rendered in a responsive context using the picture element
        context = self.super(BootstrapPicturePlugin, self).render(context, instance, placeholder)
        sources = self.get_picture_sources(instance)
        for source in sources:
            # create images for srcset in steps separated by `step_size_bytes`
            upper_image_width, upper_image_height = source['upper_bound']['width'], source['upper_bound']['height']
            upper_thumbnail_path = self.get_or_create_thumbnail(instance.image, upper_image_width, upper_image_height)
            upper_image_size = default_storage.size(upper_thumbnail_path)
            upper_image_area = upper_image_width * upper_image_height
            lower_image_width, lower_image_height = source['lower_bound']['width'], source['lower_bound']['height']
            lower_thumbnail_path = self.get_or_create_thumbnail(instance.image, lower_image_width, lower_image_height)
            lower_image_size = default_storage.size(lower_thumbnail_path)
            source['src'] = default_storage.url(lower_thumbnail_path)
            num_steps = int((upper_image_size - lower_image_size) / self.step_size_bytes) + 1
            step_size_bytes = round((upper_image_size - lower_image_size) / num_steps)
            if upper_image_width > upper_image_height:
                mult = (upper_image_width / lower_image_width) ** (1 / num_steps)
                landscape = True
            else:
                mult = (upper_image_height / lower_image_height) ** (1 / num_steps)
                landscape = False
            source['srcsets'] = [{
                'url': default_storage.url(lower_thumbnail_path),
                'width': round(lower_image_width),
                'height': round(lower_image_height),
            }]
            print(f"============ Num steps : {num_steps}. Step size: {step_size_bytes} ============")
            compression_factor = estimate_compression_factor(lower_image_width, lower_image_height, lower_image_size)
            for step in range(1 - num_steps, 0):
                wanted_image_size = upper_image_size + step * step_size_bytes
                for attempt in range(3):
                    if landscape:
                        width = sqrt(wanted_image_size / upper_image_size * source['aspect_ratio'] * compression_factor * upper_image_area)
                        height = round(width / source['aspect_ratio'])
                    else:
                        height = sqrt(wanted_image_size / upper_image_size / source['aspect_ratio'] * compression_factor * upper_image_area)
                        width = round(height * source['aspect_ratio'])
                    thumbnail_path = self.get_or_create_thumbnail(instance.image, width, height)
                    thumbnail_image_size = default_storage.size(thumbnail_path)
                    real_to_wanted_ratio = wanted_image_size / thumbnail_image_size
                    print(f"{num_steps + step} Thumbnail to {round(width)}x{round(height)}. Wanted/Real size: {wanted_image_size}/{thumbnail_image_size} = {real_to_wanted_ratio:.3f}. Compression factor: {compression_factor:.4f}.", end="")
                    if real_to_wanted_ratio >= self.real_to_wanted_ratio[0] and real_to_wanted_ratio <= self.real_to_wanted_ratio[1]:
                        # generated thumbnail is within the bounds for the wanted size
                        compression_factor = estimate_compression_factor(width, height, thumbnail_image_size) * real_to_wanted_ratio ** 4
                        print(" USED")
                        break
                    # other attempt to find a thumbnail in the wanted size
                    compression_factor = estimate_compression_factor(width, height, thumbnail_image_size)
                    ## we must keep this information: default_storage.delete(thumbnail_path)
                    print(" NOT USED")
                if width < upper_image_width and height < upper_image_height:
                    source['srcsets'].append({
                        'url': default_storage.url(thumbnail_path),
                        'width': round(width),
                        'height': round(height),
                    })
            if mult > 1.01:
                # if the step size is too small, we only use the lower bound
                source['srcsets'].append({
                    'url': default_storage.url(upper_thumbnail_path),
                    'width': round(upper_image_width),
                    'height': round(upper_image_height),
                })

        context.update({'picture': {'sources': sources, 'fallback_image': self.fallback_image}})
        return context


plugin_pool.register_plugin(BootstrapPicturePlugin)
