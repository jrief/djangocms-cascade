# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import MultipleInlineStylesWidget
from cmsplugin_cascade.image.models import ImageElement
from .plugin_base import BootstrapPluginBase
from . import settings


class ThumbnailPlugin(BootstrapPluginBase):
    name = _("Thumbnail")
    model = ImageElement
    module = 'Bootstrap'
    parent_classes = ['BootstrapColumnPlugin']
    allow_children = False
    raw_id_fields = ('image',)
    text_enabled = True
    admin_preview = False
    render_template = 'cms/plugins/generic.html'
    fields = ('image', 'glossary',)
    CLASS_CHOICES = (('thumbnail', 'Thumbnail'), ('blah', 'Blah'),)
    glossary_fields = (
        PartialFormField('css_class',
            widgets.Select(choices=CLASS_CHOICES),
            label=_('Extra Thumbnail Classes')
        ),
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['min-height']),
            label=_('Inline Styles'),
            help_text=_('Margins and minimum height for thumbnail image.')
        ),
    )

    def render(self, context, instance, placeholder):
        #screen_dimensions = self.get_screen_dimensions(context)
        max_width = self.guess_max_image_size(instance)
        context.update({
            'instance': instance,
            'placeholder': placeholder
        })
        return context

    def _responsive_image_options(self, context, instance):
        """
        Return the size and options of the thumbnail that should be inserted
        """
        width, height = None, None
        crop, upscale = False, False
        subject_location = False
        placeholder_width = context.get('width', None)
        placeholder_height = context.get('height', None)
        if instance.thumbnail_option:
            # thumbnail option overrides everything else
            if instance.thumbnail_option.width:
                width = instance.thumbnail_option.width
            if instance.thumbnail_option.height:
                height = instance.thumbnail_option.height
            crop = instance.thumbnail_option.crop
            upscale = instance.thumbnail_option.upscale
        else:
            if instance.use_autoscale and placeholder_width:
                # use the placeholder width as a hint for sizing
                width = int(placeholder_width)
            elif instance.width:
                width = instance.width
            if instance.use_autoscale and placeholder_height:
                height = int(placeholder_height)
            elif instance.height:
                height = instance.height
            crop = instance.crop
            upscale = instance.upscale
        if instance.image:
            if instance.image.subject_location:
                subject_location = instance.image.subject_location
            if not height and width:
                # height was not externally defined: use ratio to scale it by the width
                height = int( float(width)*float(instance.image.height)/float(instance.image.width) )
            if not width and height:
                # width was not externally defined: use ratio to scale it by the height
                width = int( float(height)*float(instance.image.width)/float(instance.image.height) )
            if not width:
                # width is still not defined. fallback the actual image width
                width = instance.image.width
            if not height:
                # height is still not defined. fallback the actual image height
                height = instance.image.height
        return {'size': (width, height),
                'crop': crop,
                'upscale': upscale,
                'subject_location': subject_location}

    def guess_max_image_size(self, instance):
        """
        Using the class context this image shall be rendered in, guess the maximum image size.
        Remember: In Bootstrap 3 images usually are rendered into a column, whose width is
        responsive, thus the image size shall be no more than its maximum size.
        """
        glossary = instance.get_glossary()
        breakpoints = ('lg', 'md', 'sm', 'xs')
        container_bp = glossary.get('breakpoint', 'lg')
        breakpoints = breakpoints[breakpoints.index(container_bp):]
        max_width = 0
        for bp in breakpoints:
            column_width = glossary.get('{0}-column-width'.format(bp), '').replace('col-{0}-'.format(bp), '')
            if not column_width.isdigit():
                column_width = 12
            width = settings.CMS_CASCADE_BOOTSTRAP3_COLUMN_WIDTHS[bp] * int(column_width)
            max_width = max(max_width, int(width))
        return max_width

#     def get_screen_dimensions(self, context):
#         """
#         Attempt to find out the browser's screen dimensions. This requires a cookie set by
#         the browser. This line of JavaScript code does the job:
#         document.cookie = "screen_dimensions=" + screen.width + "x" + screen.height;
#         """
#         try:
#             return context['request'].COOKIES['screen_dimensions'].split('x')
#         except (KeyError, AttributeError):
#             return settings.CMS_CASCADE_DEFAULT_SCREEN_DIMENSIONS

    @classmethod
    def get_identifier(cls, obj):
        return u'Blah blah'
        #name = obj.glossary.get('css_class').title() or cls.CLASS_CHOICES[0][1]
        #return name.title()

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(ThumbnailPlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

plugin_pool.register_plugin(ThumbnailPlugin)
