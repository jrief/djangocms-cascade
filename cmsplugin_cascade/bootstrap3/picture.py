# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms import fields
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.image.models import ImageElement
from cmsplugin_cascade.link.forms import LinkForm
from cmsplugin_cascade.link.plugin_base import LinkPluginBase
from cmsplugin_cascade.widgets import CascadingSizeWidget
from .settings import CASCADE_BREAKPOINTS_DICT


class PictureForm(LinkForm):
    TYPE_CHOICES = (('null', _("No Link")), ('int', _("Internal")), ('ext', _("External")),)
    link_type = fields.ChoiceField(choices=TYPE_CHOICES, initial='null')

    class Meta:
        model = ImageElement
        fields = ('page_link', 'image', 'glossary',)


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
    fields = ('image', 'glossary', ('link_type', 'page_link', 'url', 'email'),)
    SHAPE_CHOICES = (('img-responsive', _("Responsive")), ('img-rounded', _('Rounded')),
                     ('img-circle', _('Circle')), ('img-thumbnail', _('Thumbnail')))
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
        PartialFormField('image-shapes',
            widgets.CheckboxSelectMultiple(choices=SHAPE_CHOICES),
            label=_('Image Shapes'),
            initial='img-responsive'
        ),
        PartialFormField('image-height',
            CascadingSizeWidget(allowed_units=['px', '%']),
            label=_('Image Height'),
            initial='100%',
            help_text=_("Specifiy image height in '%' (percent) or 'px' (pixels)."),
        ),
        PartialFormField('upscale',
            widgets.CheckboxInput(),
            label=_('Upscale Image'),
            help_text=_("Upscale small images to the estimated boundaries."),
        ),
        PartialFormField('subject_location',
            widgets.CheckboxInput(),
            label=_('Subject Location'),
            initial=True,
            help_text=_("Use subject location to adjust the image's center to its most interesting part."),
        ),
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['min-height']),
            label=_('Inline Styles'),
            help_text=_('Margins and minimum height for thumbnail image.')
        ),
    )

    def render(self, context, instance, placeholder):
        appearances = self._responsive_appearances(context, instance)
        print appearances
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'appearances': appearances,
        })
        return context

    def _responsive_appearances(self, context, instance):
        complete_glossary = instance.get_complete_glossary()
        aspect_ratio = float(instance.image.height) / float(instance.image.width)
        image_height = instance.glossary['image-height'].strip()
        if image_height.endswith('%'):
            relative_height = float(image_height.rstrip('%')) / 100
            crop = relative_height < 1.0
        elif image_height.endswith('px'):
            relative_height = None
            image_height = int(image_height.rstrip('px'))
            crop = True
        else:
            raise ValueError("Image height '{0}' can't be interpreted!".format(image_height))
        upscale = instance.glossary['upscale']
        subject_location = instance.glossary['subject_location']
        min_width = 100.0
        appearance = {}
        for bp in complete_glossary['breakpoints']:
            width = float(complete_glossary['container_max_widths'][bp])
            min_width = min(min_width, round(width))
            if relative_height:
                size = (int(width), int(round(width * aspect_ratio * relative_height)))
            else:
                size = (int(width), image_height)
            appearance[bp] = self.APPEARANCE[bp]
            appearance[bp].update(size=size, crop=crop, upscale=upscale, subject_location=subject_location)
        # create a relatively small default image as fallback
        if relative_height:
            size = (int(min_width), int(round(min_width * aspect_ratio * relative_height)))
        else:
            size = (int(min_width), int(image_height))
        appearance['default'] = {'size': size, 'crop': crop, 'upscale': False, 'subject_location': False}
        return appearance

    def _get_thumbnail_options(self, context, instance):
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

    @classmethod
    def get_identifier(cls, obj):
        return u'Blah blah'
        #name = obj.glossary.get('css_class').title() or cls.CLASS_CHOICES[0][1]
        #return name.title()

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(BootstrapPicturePlugin, cls).get_css_classes(obj)
        css_class = obj.glossary.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

    @classmethod
    def x_sanitize_model(cls, obj):
        """
        By using the full glossary context this image will be rendered into, estimate the maximum
        image size. Remember: In Bootstrap 3, images usually are rendered into a column, whose width
        is responsive, thus the image size shall be no more than its maximum size.
        """
        sanitized = super(BootstrapPicturePlugin, cls).sanitize_model(obj)
        complete_glossary = obj.get_complete_glossary()
        breakpoints = ('xs', 'sm', 'md', 'lg')
        container_bp = complete_glossary.get('breakpoint', 'lg')
        breakpoints = breakpoints[:breakpoints.index(container_bp) + 1]
        estimated_max_width = obj.glossary.get('estimated_max_width')
        max_width = 0
        column_width = None
        for bp in breakpoints:
            # find out the width in column units, if missing use a smaller width
            width = complete_glossary.get('{0}-column-width'.format(bp), '').replace('col-{0}-'.format(bp), '')
            if width.isdigit():
                column_width = width
            elif column_width is None:
                column_width = 12
            # estimate the largest width in pixels this image ever might be rendered
            width = settings.CMS_CASCADE_BOOTSTRAP3_COLUMN_WIDTHS[bp] * int(column_width)
            max_width = max(max_width, int(round(width)))
        obj.glossary.update(estimated_max_width=max_width)
        return sanitized or estimated_max_width != max_width

plugin_pool.register_plugin(BootstrapPicturePlugin)
