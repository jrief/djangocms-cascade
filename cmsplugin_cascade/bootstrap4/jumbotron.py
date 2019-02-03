# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from django.core.exceptions import ValidationError
from django.forms import widgets, ModelChoiceField
from django.forms.models import ModelForm
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from filer.models.imagemodels import Image

from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.image import ImageFormMixin, ImagePropertyMixin
from cmsplugin_cascade.widgets import MultipleCascadingSizeWidget, ColorPickerWidget
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap4.container import ContainerBreakpointsWidget, ContainerGridMixin, get_widget_choices
from cmsplugin_cascade.bootstrap4.picture import BootstrapPicturePlugin, get_picture_elements
from cmsplugin_cascade.bootstrap4.grid import Breakpoint

logger = logging.getLogger('cascade')


class ImageBackgroundMixin(object):
    @property
    def background_color(self):
        try:
            disabled, color = self.glossary['background_color']
            if not disabled and disabled != 'disabled':
                return 'background-color: {};'.format(color)
        except (KeyError, TypeError, ValueError):
            pass
        return ''

    @property
    def background_attachment(self):
        try:
            return 'background-attachment: {background_attachment};'.format(**self.glossary)
        except KeyError:
            return ''

    @property
    def background_position(self):
        try:
            return 'background-position: {background_vertical_position} {background_horizontal_position};'.format(**self.glossary)
        except KeyError:
            return ''

    @property
    def background_repeat(self):
        try:
            return 'background-repeat: {background_repeat};'.format(**self.glossary)
        except KeyError:
            return ''

    @property
    def background_size(self):
        try:
            size = self.glossary['background_size']
            if size == 'width/height':
                size = self.glossary['background_width_height']
                return 'background-size: {width} {height};'.format(**size)
            else:
                return 'background-size: {};'.format(size)
        except KeyError:
            pass
        return ''


class JumbotronPluginForm(ImageFormMixin, ModelForm):
    """
    Form class to validate the JumbotronPlugin.
    """
    image_file = ModelChoiceField(queryset=Image.objects.all(), required=False, label=_("Image"))

    def clean_glossary(self):
        glossary = super(JumbotronPluginForm, self).clean_glossary()
        if glossary['background_size'] == 'width/height' and not glossary['background_width_height']['width']:
            raise ValidationError(_("You must at least set a background width."))
        return glossary


class BootstrapJumbotronPlugin(BootstrapPluginBase):
    name = _("Jumbotron")
    model_mixins = (ContainerGridMixin, ImagePropertyMixin, ImageBackgroundMixin)
    form = JumbotronPluginForm
    require_parent = False
    parent_classes = ('BootstrapColumnPlugin',)
    allow_children = True
    alien_child_classes = True
    raw_id_fields = ('image_file',)
    fields = ('glossary', 'image_file',)
    render_template = 'cascade/bootstrap4/jumbotron.html'
    ring_plugin = 'JumbotronPlugin'
    ATTACHMENT_CHOICES = ['scroll', 'fixed', 'local']
    VERTICAL_POSITION_CHOICES = ['top', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'bottom']
    HORIZONTAL_POSITION_CHOICES = ['left', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'right']
    REPEAT_CHOICES = ['repeat', 'repeat-x', 'repeat-y', 'no-repeat']
    SIZE_CHOICES = ['auto', 'width/height', 'cover', 'contain']
    container_glossary_fields = (
        GlossaryField(
            ContainerBreakpointsWidget(choices=get_widget_choices()),
            label=_("Available Breakpoints"),
            name='breakpoints',
            initial=app_settings.CMSPLUGIN_CASCADE['bootstrap4']['default_bounds'].keys(),
            help_text=_("Supported display widths for Bootstrap's grid system.")
        ),
        GlossaryField(
            MultipleCascadingSizeWidget([bp.name for bp in Breakpoint], allowed_units=['px', '%'], required=False),
            label=_("Adapt Picture Heights"),
            name='container_max_heights',
            initial={'xs': '100%', 'sm': '100%', 'md': '100%', 'lg': '100%', 'xl': '100%'},
            help_text=_("Heights of picture in percent or pixels for distinct Bootstrap's breakpoints.")
        ),
        GlossaryField(
            widgets.CheckboxSelectMultiple(choices=BootstrapPicturePlugin.RESIZE_OPTIONS),
            label=_("Resize Options"),
            name='resize_options',
            initial=['crop', 'subject_location', 'high_resolution'],
            help_text=_("Options to use when resizing the image.")
        ),
    )

    background_color = GlossaryField(
        ColorPickerWidget(),
        label=_("Background color"),
    )

    background_repeat = GlossaryField(
        widgets.RadioSelect(choices=[(c, c) for c in REPEAT_CHOICES]),
        initial='no-repeat',
        label=_("This property specifies how an image repeates."),
    )

    background_attachment = GlossaryField(
        widgets.RadioSelect(choices=[(c, c) for c in ATTACHMENT_CHOICES]),
        initial='local',
        label=_("This property specifies how to move the background relative to the viewport."),
    )

    background_vertical_position = GlossaryField(
        widgets.Select(choices=[(c, c) for c in VERTICAL_POSITION_CHOICES]),
        initial='center',
        label=_("This property moves a background image vertically within its container."),
    )

    background_horizontal_position = GlossaryField(
        widgets.Select(choices=[(c, c) for c in HORIZONTAL_POSITION_CHOICES]),
        initial='center',
        label=_("This property moves a background image horizontally within its container."),
    )

    background_size = GlossaryField(
        widgets.RadioSelect(choices=[(c, c) for c in SIZE_CHOICES]),
        initial='auto',
        label=_("Background size"),
        help_text=_("This property specifies how an image is sized."),
    )

    background_width_height = GlossaryField(
        MultipleCascadingSizeWidget(['width', 'height'], allowed_units=['px', '%'],
                                    required=False),
        label=_("Background width and height"),
        help_text=_("This property specifies the width and height of a background image."),
    )
    footnote_html = """
<p>For more information about the Jumbotron please read </p>
    """

    class Media:
        js = ['cascade/js/admin/jumbotronplugin.js']

    def get_form(self, request, obj=None, **kwargs):
        if self.get_parent_instance(request, obj) is None:
            # we only ask for breakpoints, if the jumbotron is the root of the placeholder
            kwargs.update(glossary_fields=list(self.container_glossary_fields))
            kwargs['glossary_fields'].extend(self.glossary_fields)
        form = super(BootstrapJumbotronPlugin, self).get_form(request, obj, **kwargs)
        return form

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        try:
            elements = get_picture_elements(instance)
        except Exception as exc:
            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            if instance.child_plugin_instances and instance.child_plugin_instances[0].plugin_type == 'BootstrapRowPlugin':
                padding='padding: {0}px {0}px;'.format(int( app_settings.CMSPLUGIN_CASCADE['bootstrap4']['gutter']/2))
                context.update({'add_gutter_if_child_is_BootstrapRowPlugin': padding,})
            context.update({
                'elements': [e for e in elements if 'media' in e] if elements else [],
                'CSS_PREFIXES': app_settings.CSS_PREFIXES,
            })
        return self.super(BootstrapJumbotronPlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = False
        # if the jumbotron is the root of the placeholder, we consider it as "fluid"
        obj.glossary['fluid'] = obj.parent is None
        super(BootstrapJumbotronPlugin, cls).sanitize_model(obj)
        grid_container = obj.get_bound_plugin().get_grid_instance()
        obj.glossary.setdefault('media_queries', {})
        for bp, bound in grid_container.bounds.items():
            obj.glossary['media_queries'].setdefault(bp.name, {})
            width = round(bound.max)
            if obj.glossary['media_queries'][bp.name].get('width') != width:
                obj.glossary['media_queries'][bp.name]['width'] = width
                sanitized = True
            if obj.glossary['media_queries'][bp.name].get('media') != bp.media_query:
                obj.glossary['media_queries'][bp.name]['media'] = bp.media_query
                sanitized = True
        return sanitized

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapJumbotronPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('fluid'):
            css_classes.append('jumbotron-fluid')
        else:
            css_classes.append('jumbotron')
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super(BootstrapJumbotronPlugin, cls).get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Without background image")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapJumbotronPlugin)
