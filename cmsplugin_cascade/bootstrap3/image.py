# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets, ModelChoiceField
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from filer.models.imagemodels import Image

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.image import ImageAnnotationMixin, ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.widgets import CascadingSizeWidget
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from . import utils


class BootstrapImagePlugin(ImageAnnotationMixin, LinkPluginBase):
    name = _("Image")
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    module = 'Bootstrap'
    parent_classes = ('BootstrapColumnPlugin',)
    require_parent = True
    allow_children = False
    raw_id_fields = ('image_file',)
    admin_preview = False
    ring_plugin = 'ImagePlugin'
    render_template = 'cascade/bootstrap3/linked-image.html'
    default_css_attributes = ('image_shapes',)
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    html_tag_attributes.update(LinkPluginBase.html_tag_attributes)
    fields = ['image_file'] + list(LinkPluginBase.fields)
    SHAPE_CHOICES = (('img-responsive', _("Responsive")), ('img-rounded', _('Rounded')),
                     ('img-circle', _('Circle')), ('img-thumbnail', _('Thumbnail')),)
    RESIZE_OPTIONS = (('upscale', _("Upscale image")), ('crop', _("Crop image")),
                      ('subject_location', _("With subject location")),
                      ('high_resolution', _("Optimized for Retina")),)

    image_shapes = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
        label=_("Image Shapes"),
        initial=['img-responsive']
    )

    image_width_responsive = GlossaryField(
        CascadingSizeWidget(allowed_units=['%'], required=False),
        label=_("Responsive Image Width"),
        initial='100%',
        help_text=_("Set the image width in percent relative to containing element."),
    )

    image_width_fixed = GlossaryField(
        CascadingSizeWidget(allowed_units=['px'], required=False),
        label=_("Fixed Image Width"),
        help_text=_("Set a fixed image width in pixels."),
    )

    image_height = GlossaryField(
        CascadingSizeWidget(allowed_units=['px', '%'], required=False),
        label=_("Adapt Image Height"),
        help_text=_("Set a fixed height in pixels, or percent relative to the image width."),
    )

    resize_options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
        label=_("Resize Options"),
        help_text=_("Options to use when resizing the image."),
        initial=['subject_location', 'high_resolution']
    )

    class Media:
        js = ['cascade/js/admin/imageplugin.js']

    def get_form(self, request, obj=None, **kwargs):
        utils.reduce_breakpoints(self, 'responsive_heights', request=request, obj=obj)
        LINK_TYPE_CHOICES = (('none', _("No Link")),) + \
            tuple(t for t in getattr(LinkForm, 'LINK_TYPE_CHOICES') if t[0] != 'email')
        image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))
        Form = type(str('ImageForm'), (ImageFormMixin, getattr(LinkForm, 'get_form_class')(),),
                    {'LINK_TYPE_CHOICES': LINK_TYPE_CHOICES, 'image_file': image_file})
        kwargs.update(form=Form)
        return super(BootstrapImagePlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        is_responsive = 'img-responsive' in instance.glossary.get('image_shapes', [])
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
        css_classes = cls.super(BootstrapImagePlugin, cls).get_css_classes(obj)
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
