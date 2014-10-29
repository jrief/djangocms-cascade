# -*- coding: utf-8 -*-
from django import forms
from django.forms import widgets
from django.db.models import get_model
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin.sites import site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import python_2_unicode_compatible
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import AdminFileWidget, FilerImageField
from filer.models.imagemodels import Image
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.models import LinkElementMixin
from cmsplugin_cascade.link.plugin_base import LinkPluginBase
from cmsplugin_cascade.sharable.models import SharableCascadeElement
from cmsplugin_cascade.sharable.forms import SharableGlossaryMixin
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget
from .settings import CASCADE_BREAKPOINT_APPEARANCES, CASCADE_BREAKPOINTS_LIST


class PictureForm(LinkForm):
    LINK_TYPE_CHOICES = (('none', _("No Link")), ('cmspage', _("CMS Page")), ('exturl', _("External URL")),)
    image_file = forms.ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = instance and dict(instance.glossary) or {'link': {'type': 'none'}}
        initial.update(kwargs.pop('initial', {}))
        try:
            self.base_fields['image_file'].initial = initial['image']['pk']
        except KeyError:
            self.base_fields['image_file'].initial = None
        self.base_fields['image_file'].widget = AdminFileWidget(ManyToOneRel(FilerImageField, Image, 'file_ptr'), site)
        kwargs.update(initial=initial)
        super(PictureForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PictureForm, self).clean()
        image_data = {'pk': self.cleaned_data['image_file'].pk, 'model': 'filer.Image'}
        cleaned_data['glossary'].update(image=image_data)
        del self.cleaned_data['image_file']
        return cleaned_data


@python_2_unicode_compatible
class PictureElement(LinkElementMixin, SharableCascadeElement):
    """
    A proxy model for the ``<img>`` or ``<picture>`` element wrapped in an sharable link element.
    """
    class Meta:
        proxy = True

    def __str__(self):
        return six.text_type(self.image and self.image or '')

    @property
    def image(self):
        if not hasattr(self, '_image_model'):
            Model = get_model(*self.glossary['image']['model'].split('.'))
            try:
                self._image_model = Model.objects.get(pk=self.glossary['image']['pk'])
            except (KeyError, ObjectDoesNotExist):
                self._image_model = None
        return self._image_model


class BootstrapPicturePlugin(SharableGlossaryMixin, LinkPluginBase):
    name = _("Picture")
    model = PictureElement
    form = PictureForm
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'CarouselSlidePlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = ('image_file',)
    text_enabled = True
    admin_preview = False
    render_template = 'cascade/bootstrap3/picture.html'
    default_css_attributes = ('image-shapes',)
    html_tag_attributes = {'image-title': 'title', 'alt-tag': 'tag'}
    fields = ('image_file', 'glossary', ('link_type', 'cms_page', 'ext_url',),
              ('save_shared_glossary', 'save_as_identifier'), 'shared_glossary',)
    SHAPE_CHOICES = (('img-responsive', _("Responsive")), ('img-rounded', _('Rounded')),
                     ('img-circle', _('Circle')), ('img-thumbnail', _('Thumbnail')),)
    RESIZE_OPTIONS = (('upscale', _("Upscale image")), ('crop', _("Crop image")),
                      ('subject_location', _("With subject location")),
                      ('high_resolution', _("Optimized for Retina")),)
    GLOSSARY_FIELDS = (
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
    ) + LinkPluginBase.glossary_fields + (
        PartialFormField('image-shapes',
            widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
            label=_("Image Shapes"),
            initial=['img-responsive']
        ),
        PartialFormField('image-size',
            MultipleCascadingSizeWidget(['width', 'height'], allowed_units=['px'], required=False),
            label=_("Absolute Image Sizes"),
            help_text=_("Specify an absolute image width and height in 'px' (pixels)."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['subject_location', 'high_resolution']
        ),
    )
    sharable_fields = ('image-shapes', 'image-size', 'responsive-heights', 'resize-options',)

    class Media:
        js = resolve_dependencies('cascade/js/admin/pictureplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        complete_glossary = self.get_parent_instance().get_complete_glossary()
        breakpoints = complete_glossary.get('breakpoints', CASCADE_BREAKPOINTS_LIST)
        self.glossary_fields = list(self.GLOSSARY_FIELDS[:4])
        self.glossary_fields.append(PartialFormField('responsive-heights',
            MultipleCascadingSizeWidget(breakpoints),
            label=_("Override Picture Heights"),
            initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%'},
            help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints."),
        ))
        self.glossary_fields.extend(self.GLOSSARY_FIELDS[4:])
        return super(BootstrapPicturePlugin, self).get_form(request, obj, **kwargs)

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
        container_max_heights = complete_glossary.get('container_max_heights', {})
        if instance.shared_glossary:
            resize_options = instance.shared_glossary.glossary.get('resize-options', {})
        else:
            resize_options = instance.glossary.get('resize-options', {})
        crop = 'crop' in resize_options
        upscale = 'upscale' in resize_options
        subject_location = 'subject_location' in resize_options
        min_width = 100.0
        appearances = {}
        resolutions = (False, True) if 'high_resolution' in resize_options else (False,)
        for high_res in resolutions:
            for bp in complete_glossary['breakpoints']:
                width = float(complete_glossary['container_max_widths'][bp])
                min_width = min(min_width, round(width))
                size = None
                try:
                    image_height = self._parse_responsive_height(instance.glossary['responsive-heights'][bp])
                except KeyError:
                    image_height = (None, None)
                if image_height[0]:
                    size = (int(width), image_height[0])
                elif image_height[1]:
                    size = (int(width), int(round(width * aspect_ratio * image_height[1])))
                elif bp in container_max_heights:
                    container_height = self._parse_responsive_height(container_max_heights[bp])
                    if container_height[0]:
                        size = (int(width), container_height[0])
                    elif container_height[1]:
                        size = (int(width), int(round(width * aspect_ratio * container_height[1])))
                if size is None:
                    # as fallback, adopt height to current width
                    size = (int(width), int(round(width * aspect_ratio)))
                key = high_res and bp + '-retina' or bp
                appearances[key] = CASCADE_BREAKPOINT_APPEARANCES[bp].copy()
                if high_res:
                    size = (size[0] * 2, size[1] * 2)
                    appearances[key]['media'] += ' and (min-resolution: 1.5dppx)'
                elif True in resolutions:
                    appearances[key]['media'] += ' and (max-resolution: 1.5dppx)'
                appearances[key].update(size=size, crop=crop, upscale=upscale, subject_location=subject_location)
        # create a relatively small image for the default img tag.
        if image_height[1]:
            size = (int(min_width), int(round(min_width * aspect_ratio * image_height[1])))
        else:
            size = (int(min_width), int(round(min_width * aspect_ratio)))
        default_appearance = {'size': size, 'crop': crop, 'upscale': upscale, 'subject_location': subject_location}
        return appearances, default_appearance

    def _static_appearance(self, context, instance):
        if instance.shared_glossary:
            size = instance.shared_glossary.glossary.get('image-size', {})
            resize_options = instance.shared_glossary.glossary.get('resize-options', {})
        else:
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

    @staticmethod
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

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapPicturePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

plugin_pool.register_plugin(BootstrapPicturePlugin)
