# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets, ModelChoiceField
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from filer.models.imagemodels import Image
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from . import settings, utils
from .image import ImageFormMixin

BS3_BREAKPOINT_KEYS = list(tp[0] for tp in settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])


class BootstrapPicturePlugin(LinkPluginBase):
    name = _("Picture")
    model_mixins = (ImagePropertyMixin, LinkElementMixin,)
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    allow_children = False
    raw_id_fields = ('image_file',)
    text_enabled = False
    admin_preview = False
    render_template = 'cascade/bootstrap3/linked-picture.html'
    default_css_class = 'img-responsive'
    default_css_attributes = ('image-shapes',)
    html_tag_attributes = {'image-title': 'title', 'alt-tag': 'tag'}
    fields = ('image_file', getattr(LinkPluginBase, 'glossary_field_map')['link'], 'glossary',)
    LINK_TYPE_CHOICES = (('none', _("No Link")),) + \
        tuple(t for t in getattr(LinkForm, 'LINK_TYPE_CHOICES') if t[0] != 'email')
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
        PartialFormField('responsive-heights',
            MultipleCascadingSizeWidget(BS3_BREAKPOINT_KEYS, allowed_units=['px', '%'], required=False),
            label=_("Adapt Picture Heights"),
            initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%'},
            help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints."),
        ),
        PartialFormField('responsive-zoom',
            MultipleCascadingSizeWidget(BS3_BREAKPOINT_KEYS, allowed_units=['%'], required=False),
            label=_("Adapt Picture Zoom"),
            initial={'xs': '0%', 'sm': '0%', 'md': '0%', 'lg': '0%'},
            help_text=_("Magnification of picture in percent for distinct Bootstrap's breakpoints."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['subject_location', 'high_resolution']
        ),
    )

    class Media:
        js = resolve_dependencies('cascade/js/admin/pictureplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        utils.reduce_breakpoints(self, 'responsive-heights')
        image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))
        Form = type(str('ImageForm'), (ImageFormMixin, getattr(LinkForm, 'get_form_class')(),),
            {'LINK_TYPE_CHOICES': self.LINK_TYPE_CHOICES, 'image_file': image_file})
        kwargs.update(form=Form)
        return super(BootstrapPicturePlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the picture element
        elements = utils.get_picture_elements(context, instance)
        context.update({
            'is_responsive': True,
            'instance': instance,
            'placeholder': placeholder,
            'elements': elements,
        })
        return context

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapPicturePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapPicturePlugin, cls).get_identifier(obj)
        try:
            content = force_text(obj.image)
        except AttributeError:
            content = _("No Picture")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapPicturePlugin)
