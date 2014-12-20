# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2
from django.forms import widgets
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.fields import IntegerField
from django.forms.models import ModelForm
from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.widgets import TextEditorWidget
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleCascadingSizeWidget
from .plugin_base import BootstrapPluginBase
from .settings import CASCADE_BREAKPOINTS_LIST, CASCADE_TEMPLATE_DIR
from .image import ImageForm
from .picture import BootstrapPicturePlugin
from . import utils


class CarouselSlidesForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '2', 'style': 'width: 4em;'}),
        label=_('Slides'),
        help_text=_('Number of slides for this carousel.'),
    )


class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    form = CarouselSlidesForm
    default_css_class = 'carousel'
    default_css_attributes = ('options',)
    parent_classes = ['BootstrapColumnPlugin']
    render_template = os.path.join(CASCADE_TEMPLATE_DIR, 'carousel.html')
    default_inline_styles = {'overflow': 'hidden'}
    fields = ('num_children', 'glossary',)
    DEFAULT_CAROUSEL_ATTRIBUTES = {'data-ride': 'carousel'}
    OPTION_CHOICES = (('slide', _("Animate")), ('pause', _("Pause")), ('wrap', _("Wrap")),)
    glossary_fields = (
        PartialFormField('interval',
            NumberInputWidget(attrs={'size': '2', 'style': 'width: 4em;', 'min': '1'}),
            label=_("Interval"),
            initial=5,
            help_text=_("Change slide after this number of seconds."),
        ),
        PartialFormField('options',
            widgets.CheckboxSelectMultiple(choices=OPTION_CHOICES),
            label=_('Options'),
            initial=['slide', 'wrap', 'pause'],
            help_text=_("Adjust interval for the carousel."),
        ),
        PartialFormField('container_max_heights',
            MultipleCascadingSizeWidget(CASCADE_BREAKPOINTS_LIST, allowed_units=['px']),
            label=_("Carousel heights"),
            initial={'xs': '100px', 'sm': '150px', 'md': '200px', 'lg': '300px'},
            help_text=_("Heights of Carousel in pixels for distinct Bootstrap's breakpoints."),
        ),
        PartialFormField('resize-options',
            widgets.CheckboxSelectMultiple(choices=BootstrapPicturePlugin.RESIZE_OPTIONS),
            label=_("Resize Options"),
            help_text=_("Options to use when resizing the image."),
            initial=['upscale', 'crop', 'subject_location', 'high_resolution']
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        utils.reduce_breakpoints(self, 'container_max_heights')
        return super(CarouselPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(CarouselPlugin, cls).get_identifier(obj)
        num_cols = obj.get_children().count()
        content = ungettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)
        return format_html('{0}{1}', identifier, content)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(CarouselPlugin, cls).get_css_classes(obj)
        if 'slide' in obj.glossary.get('options', []):
            css_classes.append('slide')
        return css_classes

    @classmethod
    def get_html_tag_attributes(cls, obj):
        attributes = super(CarouselPlugin, cls).get_html_tag_attributes(obj)
        attributes.update(cls.DEFAULT_CAROUSEL_ATTRIBUTES)
        attributes['data-interval'] = 1000 * int(obj.glossary.get('interval', 5))
        options = obj.glossary.get('options', [])
        attributes['data-pause'] = 'pause' in options and 'hover' or 'false'
        attributes['data-wrap'] = 'wrap' in options and 'true' or 'false'
        return attributes

    def save_model(self, request, obj, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super(CarouselPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, CarouselSlidePlugin)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(CarouselPlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        # fill all invalid heights for this container to a meaningful value
        max_height = max(obj.glossary['container_max_heights'].values())
        pattern = re.compile(r'^(\d+)px$')
        for bp in complete_glossary['breakpoints']:
            if not pattern.match(obj.glossary['container_max_heights'].get(bp, '')):
                obj.glossary['container_max_heights'][bp] = max_height
        return sanitized

plugin_pool.register_plugin(CarouselPlugin)


class CarouselSlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    model_mixins = (ImagePropertyMixin,)
    form = ImageForm
    default_css_class = 'img-responsive'
    parent_classes = ['CarouselPlugin']
    raw_id_fields = ('image_file',)
    fields = ('image_file', 'glossary',)
    render_template = os.path.join(CASCADE_TEMPLATE_DIR, 'carousel-slide.html')
    glossary_fields = (
        PartialFormField('caption',
            TextEditorWidget(),
            label=_("Slide Caption"),
            help_text=_("Caption text to be laid over the backgroud image."),
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        caption = HTMLParser().unescape(obj.glossary.get('caption', ''))
        obj.glossary.update(caption=caption)
        return super(CarouselSlidePlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        elements = utils.get_picture_elements(context, instance)
        caption = HTMLParser().unescape(instance.glossary.get('caption', ''))
        context.update({
            'is_responsive': True,
            'instance': instance,
            'caption': caption,
            'placeholder': placeholder,
            'elements': elements,
        })
        return super(CarouselSlidePlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(CarouselSlidePlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        obj.glossary.update({'resize-options': complete_glossary.get('resize-options', [])})
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(CarouselSlidePlugin, cls).get_identifier(obj)
        try:
            content = force_text(obj.image)
        except AttributeError:
            content = _("No Slide")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(CarouselSlidePlugin)
