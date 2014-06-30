# -*- coding: utf-8 -*-
import six
import json
from django import forms
from django.forms import widgets
from django.forms import fields
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.image.models import ImageElement
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase
from cmsplugin_cascade.widgets import CascadingSizeWidget, MultipleCascadingSizeWidget
from cmsplugin_cascade.common.models import SharedGlossary
from .settings import CASCADE_BREAKPOINTS_DICT


class PictureForm(LinkForm):
    TYPE_CHOICES = (('', _("No Link")), ('int', _("Internal")), ('ext', _("External")),)
    link_type = fields.ChoiceField(choices=TYPE_CHOICES, initial='')
    save_shared_glossary = fields.BooleanField(label=_("Remember image sizes as:"), required=False)
    save_as_identifier = fields.CharField(label='', required=False)

    class Meta:
        model = ImageElement
        fields = ('page_link', 'image', 'glossary',)

    def clean_save_as_identifier(self):
        identifier = self.cleaned_data['save_as_identifier']
        if SharedGlossary.objects.filter(identifier=identifier).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("The identifier '{0}' has already been used, please choose another name.").format(identifier))
        return identifier


class SelectSharedGlossary(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        if option_value:
            glossary = self.choices.queryset.get(pk=option_value).glossary
            data = format_html(' data-glossary="{0}"', json.dumps(glossary))
        else:
            data = mark_safe('')
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<option value="{0}"{1}{2}>{3}</option>',
                           option_value,
                           selected_html,
                           data,
                           force_text(option_label))


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
    fields = ('image', 'glossary', ('save_shared_glossary', 'save_as_identifier'), 'shared_glossary',
              ('link_type', 'page_link', 'url', 'email'),)
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
        LinkPluginBase.LINK_TARGET,
        PartialFormField('image-shapes',
            widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
            label=_("Image Shapes"),
            initial=['img-responsive']
        ),
    )
    shared_glossary_fields = (
        PartialFormField('image-size',
            MultipleCascadingSizeWidget(['width', 'height'], allowed_units=['px'], required=False),
            label=_("Absolute Image Sizes"),
            help_text=_("Specify an absolute image width and height in 'px' (pixels)."),
        ),
        PartialFormField('responsive-height',
            CascadingSizeWidget(allowed_units=['px', '%'], required=False),
            label=_("Override Container Height"),
            help_text=_("An optional image height in '%' (percent) or 'px' (pixels) to override the container's size."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['subject_location']
        ),
    )
    glossary_fields += shared_glossary_fields

    class Media:
        js = ['admin/js/cascade-pictureplugin.js']

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

    def get_form(self, request, obj=None, **kwargs):
        queryset = SharedGlossary.objects.filter(plugin_type=self.__class__.__name__)
        shared_glossary_choice = forms.ModelChoiceField(
            queryset=queryset,
            widget=SelectSharedGlossary(),
            label=_("Stored sizes"),
            required=False,
            empty_label=_("use sizes below"),
            help_text=_("Use remembered image sizes"))
        kwargs.update(form=type('PictureFormExtended', (kwargs.pop('form', self.form),),
                                {'shared_glossary': shared_glossary_choice}))
        return super(BootstrapPicturePlugin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # in case save_shared_glossary was set, create an entry in model SharedGlossary
        identifier = form.cleaned_data['save_as_identifier']
        if form.cleaned_data['save_shared_glossary'] and identifier:
            # move data from form glossary to shared glossary
            glossary = {}
            for field in self.shared_glossary_fields:
                if field.name in form.cleaned_data['glossary']:
                    glossary[field.name] = form.cleaned_data['glossary'][field.name]
                    del form.cleaned_data['glossary'][field.name]
            # create a new entry SharedGlossary in the database and refer to it
            shared_glossary = SharedGlossary(plugin_type=self.__class__.__name__, identifier=identifier, glossary=glossary)
            shared_glossary.save()
            obj.shared_glossary = shared_glossary
            del form.cleaned_data['shared_glossary']
        super(BootstrapPicturePlugin, self).save_model(request, obj, form, change)

    def _responsive_appearances(self, context, instance):
        """
        Create the appearance context, used to render a <picture> element which automatically adopts
        its sizes to the current column width.
        """
        complete_glossary = instance.get_complete_glossary()
        aspect_ratio = float(instance.image.height) / float(instance.image.width)
        image_height = self._parse_responsive_height(instance.glossary.get('responsive-height', ''))
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
        for bp in complete_glossary['breakpoints']:
            width = float(complete_glossary['container_max_widths'][bp])
            min_width = min(min_width, round(width))
            size = None
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
    def get_identifier(cls, obj):
        return six.u(str(obj.image))

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapPicturePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

plugin_pool.register_plugin(BootstrapPicturePlugin)
