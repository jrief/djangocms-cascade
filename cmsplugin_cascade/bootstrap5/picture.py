import logging
from math import sqrt

from django.forms import widgets, MultipleChoiceField
from django.templatetags.static import static
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _

from cms.plugin_pool import plugin_pool

from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.bootstrap5.fields import AspectRatioChoiceField
from cmsplugin_cascade.bootstrap5.mixins import AspectRatioChoicesMixin
from cmsplugin_cascade.bootstrap5.hyperlink import HyperlinkForm, HyperlinkPluginMixin, LinkTypeChoiceField
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.utils import IMAGE_SHAPE_CHOICES
from cmsplugin_cascade.link.plugin_base import LinkElementMixin

from finder.forms.fields import FinderFileField
from finder.models.file import FileModel as FinderFileModel

logger = logging.getLogger('cascade.bootstrap5')


class BootstrapPictureForm(HyperlinkForm):
    image = FinderFileField(
        accept_mime_types=['image/*'],
        label=_("Image"),
    )
    aspect_ratio = AspectRatioChoiceField(Breakpoint.xs, add_original=True)
    image_shapes = MultipleChoiceField(
        label=_("Image Shapes"),
        choices=IMAGE_SHAPE_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        required=False,
    )
    link_type = LinkTypeChoiceField(required=False)

    class Meta(HyperlinkForm.Meta):
        fields_map = {
            'glossary': [
                'image', 'aspect_ratio', 'image_shapes', *HyperlinkForm.Meta.fields_map['glossary'],
            ],
        }


class ImageElementMixin:
    """
    A mixin class to convert a CascadeElement into a proxy model for rendering an image element.
    """
    def __str__(self):
        try:
            return self.plugin_class.get_identifier(self)
        except AttributeError:
            return str(self.image)

    @cached_property
    def image(self):
        if not hasattr(self, '_image_file'):
            try:
                self._image_instance = FinderFileModel.objects.get_inode(id=self.glossary['image'], is_folder=False)
            except (KeyError, FinderFileModel.DoesNotExist):
                self._image_instance = None
        return self._image_instance


class LazySizesPictureMixin:
    """
    A mixin class to add the necessary attributes for lazy loading and responsive images using the library
    https://www.npmjs.com/package/lazysizes
    Multiple images are generated for each aspect ratio, so each image file size is approximately `step_size_bytes`
    larger than the previous one, starting from the smallest image defined by the lower bound of the source element up
    to the largest image defined by the upper bound of the source element.
    """
    default_css_class = 'lazyload img-fluid w-100'
    step_size_bytes = 48 * 1024  # thumbnail images in steps of 48kB
    min_thumbnail_width = 306
    max_thumbnail_width = 1920
    max_pixel_ratio = 2.0  # maximum pixel ratio for the image
    real_to_wanted_ratio = (0.85, 1.15)  # acceptable ratio between wanted and real thumbnail size
    fallback_image = static('cascade/fallback.svg')

    @classmethod
    def get_sources_bounds(cls, instance):
        """
        Determine the lower and upper bounds for each ``<source>`` in the ``<picture>`` element.
        """

        allowed_breakpoints = cls.get_breakpoints(instance)
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
                width = min(cls.min_thumbnail_width, instance.image.width)
                height = min(width / computed_aspect_ratio, instance.image.height)
                source_element = {
                    'aspect_ratio': computed_aspect_ratio,
                    'min_width': f"{breakpoint.min_width}px" if breakpoint.min_width else None,
                    'lower_bound': {'width': width, 'height': height},
                }
                sources.append(source_element)

            source_element['max_width'] = f"{breakpoint.max_width - 0.02}px" if breakpoint.max_width else None
            width = breakpoint.max_width if breakpoint.max_width else cls.max_thumbnail_width
            width = min(width * cls.max_pixel_ratio, instance.image.width)
            height = width / computed_aspect_ratio
            if height > instance.image.height:
                height = instance.image.height
                width = height * computed_aspect_ratio
            source_element['upper_bound'] = {'width': width, 'height': height}
            prev_aspect_ratio = aspect_ratio

        return sources

    @classmethod
    def get_or_create_cropped(cls, ambit, image, width, height):
        width, height = min(round(width), image.width), min(round(height), image.height)
        cropped_filename = image.get_cropped_filename(width, height)
        thumbnail_path = f'{image.id}/{cropped_filename}'
        if not ambit.sample_storage.exists(thumbnail_path):
            try:
                image.crop(ambit, thumbnail_path, width, height)
            except Exception as exception:
                logger.warning(f"Thumbnail generation failed for image {image}: {exception}")
                return None
        return thumbnail_path

    @classmethod
    def get_picture_sources(cls, instance):
        def estimate_compression_factor(crop_width, crop_height, crop_size):
            pixel_ratio = round(crop_width) * round(crop_height) / largest_image_area
            return largest_image_size * pixel_ratio / crop_size

        # image shall be rendered in a responsive context using the picture element
        ambit = instance.image.folder.get_ambit()
        sources = cls.get_sources_bounds(instance)
        for source in sources:
            # create images for srcset in steps separated by `step_size_bytes`
            largest_image_width, largest_image_height = source['upper_bound']['width'], source['upper_bound']['height']
            largest_image_path = cls.get_or_create_cropped(ambit, instance.image, largest_image_width, largest_image_height)
            smallest_image_width, smallest_image_height = source['lower_bound']['width'], source['lower_bound']['height']
            smallest_image_path = cls.get_or_create_cropped(ambit, instance.image, smallest_image_width, smallest_image_height)
            if not largest_image_path or not smallest_image_path:
                continue
            largest_image_size = ambit.sample_storage.size(largest_image_path)
            largest_image_area = largest_image_width * largest_image_height
            smallest_image_size = ambit.sample_storage.size(smallest_image_path)
            source['src'] = ambit.sample_storage.url(smallest_image_path)
            num_steps = int((largest_image_size - smallest_image_size) / cls.step_size_bytes) + 1
            step_size_bytes = round((largest_image_size - smallest_image_size) / num_steps)
            if largest_image_width > largest_image_height:
                mult = (largest_image_width / smallest_image_width) ** (1 / num_steps)
                landscape = True
            else:
                mult = (largest_image_height / smallest_image_height) ** (1 / num_steps)
                landscape = False
            source['srcsets'] = [{
                'url': ambit.sample_storage.url(smallest_image_path),
                'width': round(smallest_image_width),
                'height': round(smallest_image_height),
            }]
            logger.debug(
                "==== Num steps : {num_steps}. Step size: {step_size_bytes}",
                num_steps=num_steps,
                step_size_bytes=step_size_bytes,
            )
            compression_factor = estimate_compression_factor(smallest_image_width, smallest_image_height, smallest_image_size)

            # create a set of images in different files sizes, guess width and height to find the right size
            for step in range(1 - num_steps, 0):
                wanted_image_size = largest_image_size + step * step_size_bytes
                for attempt in range(3):
                    if landscape:
                        width = sqrt(wanted_image_size / largest_image_size * source['aspect_ratio'] * compression_factor * largest_image_area)
                        height = round(width / source['aspect_ratio'])
                    else:
                        height = sqrt(wanted_image_size / largest_image_size / source['aspect_ratio'] * compression_factor * largest_image_area)
                        width = round(height * source['aspect_ratio'])
                    cropped_image_path = cls.get_or_create_cropped(ambit, instance.image, width, height)
                    cropped_image_size = ambit.sample_storage.size(cropped_image_path)
                    real_to_wanted_ratio = wanted_image_size / cropped_image_size
                    logger.debug(
                        " - {step_num} Thumbnail to {width}x{height}. "
                        "Wanted/Real size: {wanted_image_size}/{cropped_image_size} = {real_to_wanted_ratio:.0f}%. "
                        "Compression factor: {compression_factor:.4f}.",
                        step_num=num_steps + step,
                        width=round(width),
                        height=round(height),
                        wanted_image_size=wanted_image_size,
                        cropped_image_size=cropped_image_size,
                        real_to_wanted_ratio=100 * real_to_wanted_ratio,
                        compression_factor=compression_factor,
                    )
                    if real_to_wanted_ratio >= cls.real_to_wanted_ratio[0] and real_to_wanted_ratio <= cls.real_to_wanted_ratio[1]:
                        # generated thumbnail is within the bounds for the wanted size
                        compression_factor = estimate_compression_factor(width, height, cropped_image_size) * real_to_wanted_ratio ** 4
                        break
                    # perform another attempt to find a thumbnail in the wanted size
                    compression_factor = estimate_compression_factor(width, height, cropped_image_size)
                    ambit.sample_storage.delete(cropped_image_path)
                if width < largest_image_width and height < largest_image_height:
                    source['srcsets'].append({
                        'url': ambit.sample_storage.url(cropped_image_path),
                        'width': round(width),
                        'height': round(height),
                    })
            if mult > 1.01:
                # if the step size is too small, only use the lower bound
                source['srcsets'].append({
                    'url': ambit.sample_storage.url(largest_image_path),
                    'width': round(largest_image_width),
                    'height': round(largest_image_height),
                })

        return sources


class BootstrapPicturePlugin(HyperlinkPluginMixin, AspectRatioChoicesMixin, LazySizesPictureMixin, BootstrapPluginBase):
    name = _("Picture")
    module = 'Bootstrap'
    parent_classes = ['BootstrapAccordionItemPlugin', 'BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    allow_children = False
    model_mixins = (LinkElementMixin, ImageElementMixin)
    admin_preview = False
    form = BootstrapPictureForm
    render_template = 'cascade/bootstrap5/picturelink.html'
    default_css_attributes = ['image_shapes']
    default_css_class = 'lazyload w-100'
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

    def render(self, context, instance, placeholder):
        """
        Create a context, used to render a <picture> together with all its ``<source>`` elements:
        It returns a list of HTML elements, each containing the information to render a ``<source>``
        element. If no art direction is required, the rendered HTML element collapses to a simple
        ``<img>`` with ``srcset`` and ``sizes`` attributes.
        """

        if not (sources := instance.glossary.get('cached_sources')):
            sources = self.get_picture_sources(instance)
            instance.glossary['cached_sources'] = sources
            instance.save(update_fields=['glossary'])

        context = self.super(BootstrapPicturePlugin, self).render(context, instance, placeholder)
        if instance.image:
            if not (alt_text := instance.image.meta_data.get(f'alt_text_{instance.language}')):
                alt_text = instance.image.meta_data.get('alt_text', instance.image.name)
        else:
            alt_text = ""
        context.update({'picture': {'sources': sources, 'fallback_image': self.fallback_image, 'alt': alt_text}})
        return context

    def save_model(self, request, obj, form, change):
        obj.glossary.pop('cached_sources', None)
        return super().save_model(request, obj, form, change)


plugin_pool.register_plugin(BootstrapPicturePlugin)
