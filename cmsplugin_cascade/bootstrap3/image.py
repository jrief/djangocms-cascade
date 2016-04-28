# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets, ModelChoiceField
from django.forms.models import ModelForm
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin.sites import site
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import AdminFileWidget, FilerImageField
from filer.models.imagemodels import Image
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.widgets import CascadingSizeWidget
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from . import utils


class ImageFormMixin(object):
    def __init__(self, *args, **kwargs):
        try:
            self.base_fields['image_file'].initial = kwargs['instance'].image.pk
        except (AttributeError, KeyError):
            self.base_fields['image_file'].initial = None
        self.base_fields['image_file'].widget = AdminFileWidget(ManyToOneRel(FilerImageField, Image, 'file_ptr'), site)
        super(ImageFormMixin, self).__init__(*args, **kwargs)

    def clean_glossary(self):
        assert isinstance(self.cleaned_data['glossary'], dict)
        return self.cleaned_data['glossary']

    def clean(self):
        cleaned_data = super(ImageFormMixin, self).clean()
        if self.is_valid() and cleaned_data['image_file']:
            image_data = {'pk': cleaned_data['image_file'].pk, 'model': 'filer.Image'}
            cleaned_data['glossary'].update(image=image_data)
        self.cleaned_data.pop('image_file', None)
        return cleaned_data


class ImageForm(ImageFormMixin, ModelForm):
    image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))


class BootstrapImagePlugin(LinkPluginBase):
    name = _("Image")
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = ('image_file',)
    text_enabled = True
    admin_preview = False
    render_template = 'cascade/bootstrap3/linked-image.html'
    default_css_attributes = ('image-shapes',)
    html_tag_attributes = {'image-title': 'title', 'alt-tag': 'tag'}
    fields = ('image_file', getattr(LinkPluginBase, 'glossary_field_map')['link'], 'glossary',)
    LINK_TYPE_CHOICES = (('none', _("No Link")),) + \
        tuple(t for t in getattr(LinkForm, 'LINK_TYPE_CHOICES') if t[0] != 'email')
    SHAPE_CHOICES = (('img-responsive', _("Responsive")), ('img-rounded', _('Rounded')),
                     ('img-circle', _('Circle')), ('img-thumbnail', _('Thumbnail')),)
    RESIZE_OPTIONS = (('upscale', _("Upscale image")), ('crop', _("Crop image")),
                      ('subject_location', _("With subject location")),
                      ('high_resolution', _("Optimized for Retina")),)
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
    ) + getattr(LinkPluginBase, 'glossary_fields', ()) + (
        PartialFormField('image-shapes',
            widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
            label=_("Image Shapes"),
            initial=['img-responsive']
        ),
        PartialFormField('image-width-responsive',
            CascadingSizeWidget(allowed_units=['%'], required=False),
            label=_("Responsive Image Width"),
            initial='100%',
            help_text=_("Set the image width in percent relative to containing element."),
        ),
        PartialFormField('image-width-fixed',
            CascadingSizeWidget(allowed_units=['px'], required=False),
            label=_("Fixed Image Width"),
            help_text=_("Set a fixed image width in pixels."),
        ),
        PartialFormField('image-height',
            CascadingSizeWidget(allowed_units=['px', '%'], required=False),
            label=_("Adapt Image Height"),
            help_text=_("Set a fixed height in pixels, or percent relative to the image width."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['subject_location', 'high_resolution']
        ),
    )

    class Media:
        js = resolve_dependencies('cascade/js/admin/imageplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        utils.reduce_breakpoints(self, 'responsive-heights')
        image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))
        Form = type(str('ImageForm'), (ImageFormMixin, getattr(LinkForm, 'get_form_class')(),),
            {'LINK_TYPE_CHOICES': self.LINK_TYPE_CHOICES, 'image_file': image_file})
        kwargs.update(form=Form)
        return super(BootstrapImagePlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        is_responsive = 'img-responsive' in instance.glossary.get('image-shapes', [])
        options = dict(instance.get_complete_glossary(), is_responsive=is_responsive)
        tags = utils.get_image_tags(context, instance, options)
        if tags:
            extra_styles = tags.pop('extra_styles')
            inline_styles = instance.glossary.get('inline_styles', {})
            inline_styles.update(extra_styles)
            instance.glossary['inline_styles'] = inline_styles
            context.update(dict(instance=instance, placeholder=placeholder, **tags))
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapImagePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapImagePlugin, cls).get_identifier(obj)
        try:
            content = force_text(obj.image)
        except AttributeError:
            content = _("No Image")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapImagePlugin)
