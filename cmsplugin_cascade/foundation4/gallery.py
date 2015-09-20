# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets, ModelChoiceField, CharField
from django.forms.models import ModelForm
from django.db.models.fields.related import ManyToOneRel
from django.contrib.admin import StackedInline
from django.contrib.admin.sites import site
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from filer.fields.image import AdminFileWidget, FilerImageField
from filer.models.imagemodels import Image
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.models import InlineCascadeElement
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.plugin_base import CascadePluginBase, create_proxy_model
from cmsplugin_cascade.widgets import CascadingSizeWidget
from . import utils


class GalleryImageForm(ModelForm):
    image_file = ModelChoiceField(queryset=Image.objects.all(), label=_("Image"), required=False)
    image_title = CharField(label=_("Image Title"), required=False,
            widget=widgets.TextInput(attrs={'size': 60}),
            help_text=_("Caption text added to the 'title' attribute of the <img> element."))
    alt_tag = CharField(label=_("Alternative Description"), required=False,
            widget=widgets.TextInput(attrs={'size': 60}),
            help_text=_("Textual description of the image added to the 'alt' tag of the <img> element."))
    glossary_fields = ('image_title', 'alt_tag',)

    class Meta:
        exclude = ('glossary',)

    def __init__(self, *args, **kwargs):
        try:
            initial = dict(kwargs['instance'].glossary)
        except (KeyError, AttributeError):
            initial = {}
        initial.update(kwargs.pop('initial', {}))
        for key in self.glossary_fields:
            self.base_fields[key].initial = initial.get(key)
        try:
            self.base_fields['image_file'].initial = initial['image']['pk']
        except KeyError:
            self.base_fields['image_file'].initial = None
        self.base_fields['image_file'].widget = AdminFileWidget(ManyToOneRel(FilerImageField, Image, 'file_ptr'), site)
        super(GalleryImageForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(GalleryImageForm, self).clean()
        if self.is_valid():
            image_file = self.cleaned_data.pop('image_file', None)
            if image_file:
                image_data = {'pk': image_file.pk, 'model': 'filer.Image'}
                self.instance.glossary.update(image=image_data)
            else:
                self.instance.glossary.pop('image', None)
            for key in self.glossary_fields:
                self.instance.glossary.update({key: cleaned_data.pop(key, '')})
        return cleaned_data


class GalleryPluginInline(StackedInline):
    model = InlineCascadeElement
    raw_id_fields = ('image_file',)
    form = GalleryImageForm
    extra = 0


class BootstrapGalleryPlugin(CascadePluginBase):
    name = _("Gallery")
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = ('image_file',)
    text_enabled = True
    admin_preview = False
    render_template = 'cascade/bootstrap3/gallery.html'
    default_css_attributes = ('image-shapes',)
    html_tag_attributes = {'image-title': 'title', 'alt-tag': 'tag'}
    inlines = (GalleryPluginInline,)
    SHAPE_CHOICES = (('img-responsive', _("Responsive")),)
    RESIZE_OPTIONS = (('upscale', _("Upscale image")), ('crop', _("Crop image")),
                      ('subject_location', _("With subject location")),
                      ('high_resolution', _("Optimized for Retina")),)
    glossary_fields = (
        PartialFormField('image-shapes',
            widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
            label=_("Image Responsiveness"),
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
        PartialFormField('thumbnail-width',
            CascadingSizeWidget(allowed_units=['px']),
            label=_("Thumbnail Width"),
            help_text=_("Set a fixed thumbnail width in pixels."),
        ),
        PartialFormField('thumbnail-height',
            CascadingSizeWidget(allowed_units=['px', '%']),
            label=_("Thumbnail Height"),
            help_text=_("Set a fixed height in pixels, or percent relative to the thumbnail width."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['crop', 'subject_location', 'high_resolution']
        ),
    )

    class Media:
        js = resolve_dependencies('cascade/js/admin/imageplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        utils.reduce_breakpoints(self, 'responsive-heights')
        form = super(BootstrapGalleryPlugin, self).get_form(request, obj, **kwargs)
        return form

    def render(self, context, instance, placeholder):
        gallery_instances = []
        options = dict(instance.get_complete_glossary())
        for inline_element in instance.inline_elements.all():
            # since inline_element requires the property `image`, add ImagePropertyMixin
            # to its class during runtime
            try:
                ProxyModel = create_proxy_model('GalleryImage', (ImagePropertyMixin,), InlineCascadeElement)
                inline_element.__class__ = ProxyModel
                options.update(inline_element.glossary, **{
                    'image-width-fixed': options['thumbnail-width'],
                    'image-height': options['thumbnail-height'],
                    'is_responsive': False,
                })
                thumbnail_tags = utils.get_image_tags(context, inline_element, options)
                for key, val in thumbnail_tags.items():
                    setattr(inline_element, key, val)
                gallery_instances.append(inline_element)
            except (KeyError, AttributeError):
                pass
        inline_styles = instance.glossary.get('inline_styles', {})
        inline_styles.update(width=options['thumbnail-width'])
        instance.glossary['inline_styles'] = inline_styles
        context.update(dict(instance=instance, placeholder=placeholder, gallery_instances=gallery_instances))
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapGalleryPlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapGalleryPlugin, cls).get_identifier(obj)
        num_elems = obj.inline_elements.count()
        content = ungettext_lazy("with {0} image", "with {0} images", num_elems).format(num_elems)
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapGalleryPlugin)
