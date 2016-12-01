# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion
import re
try:
    from html.parser import HTMLParser  # py3
except ImportError:
    from HTMLParser import HTMLParser  # py2

from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.fields import IntegerField
from django.forms.models import ModelForm

from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor import __version__ as djangocms_text_ckeditor_version
from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.utils import plugin_tags_to_user_html

from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleCascadingSizeWidget
from cmsplugin_cascade.link.cms_plugins import TextLinkPlugin
from . import settings, utils
from .plugin_base import BootstrapPluginBase
from .image import ImageForm
from .picture import BootstrapPicturePlugin

# These means "less than or equal to CKEDITOR_FOO_BAR"
CKEDITOR_3_2_0 = LooseVersion(djangocms_text_ckeditor_version) < LooseVersion("3.2.1")

class CarouselSlidesForm(ManageChildrenFormMixin, ModelForm):
    num_children = IntegerField(min_value=1, initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        label=_('Slides'),
        help_text=_('Number of slides for this carousel.'),
    )


class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    form = CarouselSlidesForm
    default_css_class = 'carousel'
    default_css_attributes = ('options',)
    parent_classes = ['BootstrapColumnPlugin', 'SimpleWrapperPlugin']
    render_template = 'cascade/bootstrap3/{}/carousel.html'
    default_inline_styles = {'overflow': 'hidden'}
    fields = ('num_children', 'glossary',)
    DEFAULT_CAROUSEL_ATTRIBUTES = {'data-ride': 'carousel'}
    OPTION_CHOICES = (('slide', _("Animate")), ('pause', _("Pause")), ('wrap', _("Wrap")),)

    interval = GlossaryField(
        NumberInputWidget(attrs={'size': '2', 'style': 'width: 4em;', 'min': '1'}),
        label=_("Interval"),
        initial=5,
        help_text=_("Change slide after this number of seconds."),
    )

    options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=OPTION_CHOICES),
        label=_('Options'),
        initial=['slide', 'wrap', 'pause'],
        help_text=_("Adjust interval for the carousel."),
    )

    container_max_heights = GlossaryField(
        MultipleCascadingSizeWidget(list(tp[0] for tp in settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints']),
        allowed_units=['px']),
        label=_("Carousel heights"),
        initial=dict((bp[0], '{}px'.format(100 + 50 * i))
            for i, bp in enumerate(settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])),
        help_text=_("Heights of Carousel in pixels for distinct Bootstrap's breakpoints."),
    )

    resize_options = GlossaryField(
        widgets.CheckboxSelectMultiple(choices=BootstrapPicturePlugin.RESIZE_OPTIONS),
        label=_("Resize Options"),
        help_text=_("Options to use when resizing the image."),
        initial=['upscale', 'crop', 'subject_location', 'high_resolution']
    )

    def get_form(self, request, obj=None, **kwargs):
        utils.reduce_breakpoints(self, 'container_max_heights', request)
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
        for bp in complete_glossary.get('breakpoints', ()):
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
    allow_children = True
    alien_child_classes = True
    raw_id_fields = ('image_file',)
    fields = ('image_file', 'glossary',)
    render_template = 'cascade/bootstrap3/carousel-slide.html'
    change_form_template = 'cascade/admin/text_plugin_change_form.html'
    html_parser = HTMLParser()

    def get_form(self, request, obj=None, **kwargs):
        parent_obj = self.get_parent_instance(request, obj)
        if not (parent_obj and issubclass(parent_obj.plugin_class, BootstrapPluginBase)):
            raise ImproperlyConfigured("A CarouselSlidePlugin requires a valid parent")

        if (CKEDITOR_3_2_0):
            # define glossary fields on the fly, because the TextEditorWidget requires the plugin_pk
            text_editor_widget = TextEditorWidget(installed_plugins=[TextLinkPlugin], pk=obj.pk,
                                                  placeholder=obj.placeholder,
                                                  plugin_language=obj.language)
            caption = GlossaryField(
                text_editor_widget,
                label=_("Slide Caption"), name='caption',
                help_text=_("Caption text to be laid over the backgroud image.")
            )
        else:
            if obj:
                caption = self.html_parser.unescape(obj.glossary.get('caption', ''))
                obj.glossary.update(caption=caption)

                if caption:
                    caption = GlossaryField(
                        widgets.TextInput(attrs={'size': 150}),
                        label=_("Slide Caption"), name='caption',
                        help_text=_("Caption text to be laid over the backgroud image.")
                    )
                else:
                    caption = GlossaryField(
                        widgets.TextInput(attrs={'hidden': True}),
                        name=''
                    )
            else:
                caption = GlossaryField(
                    widgets.TextInput(attrs={'hidden': True}),
                    name=''
                )

        kwargs['glossary_fields'] = (caption,)

        return super(CarouselSlidePlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        elements = utils.get_picture_elements(context, instance)
        caption = self.html_parser.unescape(instance.glossary.get('caption', ''))
        fluid = instance.get_complete_glossary().get('fluid') == 'on'
        if caption:
            if CKEDITOR_3_2_0:
                caption = plugin_tags_to_user_html(caption, context, placeholder)
            else:
                caption = plugin_tags_to_user_html(caption, context)
        context.update({
            'is_responsive': True,
            'instance'     : instance,
            'caption'      : caption,
            'is_fluid'     : fluid,
            'placeholder'  : placeholder,
            'elements'     : elements,
        })
        return super(CarouselSlidePlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = super(CarouselSlidePlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        obj.glossary.update({'resize_options': complete_glossary.get('resize_options', [])})
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(CarouselSlidePlugin, cls).get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Empty Slide")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(CarouselSlidePlugin)
