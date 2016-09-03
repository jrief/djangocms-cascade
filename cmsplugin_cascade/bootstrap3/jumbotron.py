# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.mixins import ImagePropertyMixin
from cmsplugin_cascade.utils import resolve_dependencies
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget, ColorPickerWidget
from .plugin_base import BootstrapPluginBase
from .image import ImageForm
from .utils import get_widget_choices, compute_media_queries, get_picture_elements, BS3_BREAKPOINT_KEYS
from .container import ContainerBreakpointsRenderer
from .picture import BootstrapPicturePlugin


class ImageBackgroundMixin(object):
    @property
    def background_color(self):
        try:
            disabled, color = self.glossary['background-color']
            if not disabled and disabled != 'disabled':
                return 'background-color: {};'.format(color)
        except (KeyError, TypeError, ValueError):
            pass
        return ''

    @property
    def background_attachment(self):
        try:
            return 'background-attachment: {background-attachment};'.format(**self.glossary)
        except KeyError:
            return ''

    @property
    def background_position(self):
        try:
            return 'background-position: {background-vertical-position} {background-horizontal-position};'.format(**self.glossary)
        except KeyError:
            return ''

    @property
    def background_repeat(self):
        try:
            return 'background-repeat: {background-repeat};'.format(**self.glossary)
        except KeyError:
            return ''

    @property
    def background_size(self):
        try:
            size = self.glossary['background-size']
            if size == 'width/height':
                size = self.glossary['background-width-height']
                return 'background-size: {width} {height};'.format(**size)
            else:
                return 'background-size: {};'.format(size)
        except KeyError:
            pass
        return ''


class JumbotronPluginForm(ImageForm):
    """
    Form class to validate the JumbotronPlugin.
    """
    def clean_glossary(self):
        glossary = super(JumbotronPluginForm, self).clean_glossary()
        if glossary['background-size'] == 'width/height' and not glossary['background-width-height']['width']:
            raise ValidationError(_("You must at least set a background width."))
        return glossary


class BootstrapJumbotronPlugin(BootstrapPluginBase):
    name = _("Jumbotron")
    model_mixins = (ImagePropertyMixin, ImageBackgroundMixin)
    form = JumbotronPluginForm
    default_css_class = 'jumbotron'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = False
    allow_children = True
    alien_child_classes = True
    raw_id_fields = ('image_file',)
    fields = ('glossary', 'image_file',)
    render_template = 'cascade/bootstrap3/jumbotron.html'
    ATTACHMENT_CHOICES = ('scroll', 'fixed', 'local')
    VERTICAL_POSITION_CHOICES = ('top', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'bottom')
    HORIZONTAL_POSITION_CHOICES = ('left', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'right')
    REPEAT_CHOICES = ('repeat', 'repeat-x', 'repeat-y', 'no-repeat')
    SIZE_CHOICES = ('auto', 'width/height', 'cover', 'contain')
    container_glossary_fields = (
        PartialFormField(
           'breakpoints',
            widgets.CheckboxSelectMultiple(choices=get_widget_choices(),
                                           renderer=ContainerBreakpointsRenderer),
            label=_("Available Breakpoints"),
            initial=list(BS3_BREAKPOINT_KEYS)[::-1],
            help_text=_("Supported display widths for Bootstrap's grid system.")
        ),
        PartialFormField(
            'container_max_heights',
            MultipleCascadingSizeWidget(BS3_BREAKPOINT_KEYS,
                                        allowed_units=['px', '%'], required=False),
            label=_("Adapt Picture Heights"),
            initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%'},
            help_text=_(
                "Heights of picture in percent or pixels for distinct Bootstrap's breakpoints."),
        ),
        PartialFormField(
            'resize-options',
             widgets.CheckboxSelectMultiple(choices=BootstrapPicturePlugin.RESIZE_OPTIONS),
             label=_("Resize Options"),
             help_text=_("Options to use when resizing the image."),
             initial=['crop', 'subject_location', 'high_resolution']
        ),
    )
    glossary_fields = (
        PartialFormField(
            'background-color',
            ColorPickerWidget(),
            label=_("Background color"),
        ),
        PartialFormField(
            'background-repeat',
            widgets.RadioSelect(choices=[(c, c) for c in REPEAT_CHOICES]),
            initial='no-repeat',
            label=_("This property specifies how an image repeates."),
        ),
        PartialFormField(
            'background-attachment',
            widgets.RadioSelect(choices=[(c, c) for c in ATTACHMENT_CHOICES]),
            initial='local',
            label=_("This property specifies how to move the background relative to the viewport."),
        ),
        PartialFormField(
            'background-vertical-position',
            widgets.Select(choices=[(c, c) for c in VERTICAL_POSITION_CHOICES]),
            initial='center',
            label=_("This property moves a background image vertically within its container."),
        ),
        PartialFormField(
            'background-horizontal-position',
            widgets.Select(choices=[(c, c) for c in HORIZONTAL_POSITION_CHOICES]),
            initial='center',
            label=_("This property moves a background image horizontally within its container."),
        ),
        PartialFormField(
            'background-size',
            widgets.RadioSelect(choices=[(c, c) for c in SIZE_CHOICES]),
            initial='auto',
            label=_("Background size"),
            help_text=_("This property specifies how an image is sized."),
        ),
        PartialFormField(
            'background-width-height',
            MultipleCascadingSizeWidget(['width', 'height'], allowed_units=['px', '%'],
                                        required=False),
            label=_("Background width and height"),
            help_text=_("This property specifies the width and height of a background image."),
        ),
    )
    footnote_html = """
<p>For more information about the Jumbotron please read </p>
    """

    class Media:
        css = {'all': (settings.CMSPLUGIN_CASCADE['fontawesome_css_url'],)}
        js = resolve_dependencies('cascade/js/admin/jumbotronplugin.js')

    def get_form(self, request, obj=None, **kwargs):
        if self.get_parent_instance(request) is None:
            # we only ask for breakpoints, if the jumbotron is the root of the placeholder
            kwargs.update(glossary_fields=list(self.container_glossary_fields))
            kwargs['glossary_fields'].extend(self.glossary_fields)
        form = super(BootstrapJumbotronPlugin, self).get_form(request, obj, **kwargs)
        return form

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        elements = get_picture_elements(context, instance)
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'elements': [e for e in elements if 'media' in e] if elements else [],
        })
        return super(BootstrapJumbotronPlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        # if the jumbotron is the root of the placeholder, we consider it as "fluid"
        obj.glossary['fluid'] = obj.parent is None
        sanitized = super(BootstrapJumbotronPlugin, cls).sanitize_model(obj)
        compute_media_queries(obj)
        return sanitized

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapJumbotronPlugin, cls).get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Without background image")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapJumbotronPlugin)
