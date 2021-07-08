import logging
from django.core.exceptions import ValidationError
from django.forms import widgets, BooleanField, ChoiceField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from entangled.forms import EntangledModelFormMixin

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import app_settings
from cmsplugin_cascade.fields import ColorField, MultiSizeField, CascadeImageField
from cmsplugin_cascade.image import ImagePropertyMixin
from cmsplugin_cascade.bootstrap4.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap4.container import ContainerGridMixin
from cmsplugin_cascade.bootstrap4.fields import BootstrapMultiSizeField
from cmsplugin_cascade.bootstrap4.picture import get_picture_elements

logger = logging.getLogger('cascade')


class ImageBackgroundMixin:
    @property
    def element_heights(self):
        element_heights = self.glossary.get('element_heights', {})
        for bp, media_query in self.glossary['media_queries'].items():
            if bp in element_heights:
                yield {'media': media_query['media'], 'height': element_heights[bp]}

    @property
    def background_color(self):
        try:
            color, disabled = self.glossary['background_color']
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


class JumbotronFormMixin(EntangledModelFormMixin):
    """
    Form class to validate the JumbotronPlugin.
    """
    ATTACHMENT_CHOICES = ['scroll', 'fixed', 'local']
    VERTICAL_POSITION_CHOICES = ['top', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'bottom']
    HORIZONTAL_POSITION_CHOICES = ['left', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'right']
    REPEAT_CHOICES = ['repeat', 'repeat-x', 'repeat-y', 'no-repeat']
    SIZE_CHOICES = ['auto', 'width/height', 'cover', 'contain']

    fluid = BooleanField(
        label=_("Is fluid"),
        initial=True,
        required=False,
        help_text=_("Shall this element occupy the entire horizontal space of its parent."),
    )

    element_heights = BootstrapMultiSizeField(
        label=("Element Heights"),
        required=True,
        allowed_units=['rem', 'px', 'auto'],
        initial='300px',
        help_text=_("This property specifies the height for each Bootstrap breakpoint."),
    )

    background_color = ColorField(
        label=_("Background color"),
    )

    image_file = CascadeImageField(
        label=_("Background image"),
        required=False,
    )

    background_repeat = ChoiceField(
        label=_("Background repeat"),
        choices=[(c, c) for c in REPEAT_CHOICES],
        widget=widgets.RadioSelect,
        initial='no-repeat',
        required=False,
        help_text=_("This property specifies how the background image repeates."),
    )

    background_attachment = ChoiceField(
        label=_("Background attachment"),
        choices=[(c, c) for c in ATTACHMENT_CHOICES],
        widget=widgets.RadioSelect,
        initial='local',
        required=False,
        help_text=_("This property specifies how to move the background image relative to the viewport."),
    )

    background_vertical_position = ChoiceField(
        label=_("Background vertical position"),
        choices=[(c, c) for c in VERTICAL_POSITION_CHOICES],
        initial='center',
        required=False,
        help_text=_("This property moves a background image vertically within its container."),
    )

    background_horizontal_position = ChoiceField(
        label=_("Background horizontal position"),
        choices=[(c, c) for c in HORIZONTAL_POSITION_CHOICES],
        initial='center',
        required=False,
        help_text=_("This property moves a background image horizontally within its container."),
    )

    background_size = ChoiceField(
        label=_("Background size"),
        choices=[(c, c) for c in SIZE_CHOICES],
        widget=widgets.RadioSelect,
        initial='auto',
        required=False,
        help_text=_("This property specifies how the background image is sized."),
    )

    background_width_height = MultiSizeField(
        ['width', 'height'],
        label=_("Background width/height"),
        allowed_units=['px', '%'],
        required=False,
        help_text=_("This property specifies the width and height of a background image in px or %."),
    )

    class Meta:
        entangled_fields = {'glossary': ['fluid', 'background_color', 'element_heights', 'image_file',
                                         'background_repeat', 'background_attachment',
                                         'background_vertical_position', 'background_horizontal_position',
                                         'background_size', 'background_width_height']}

    def validate_optional_field(self, name):
        field = self.fields[name]
        value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
        if value in field.empty_values:
            self.add_error(name, ValidationError(field.error_messages['required'], code='required'))
        else:
            return value

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['image_file']:
            self.validate_optional_field('background_repeat')
            self.validate_optional_field('background_attachment')
            self.validate_optional_field('background_vertical_position')
            self.validate_optional_field('background_horizontal_position')
            if self.validate_optional_field('background_size') == 'width/height':
                try:
                    cleaned_data['background_width_height']['width']
                except KeyError:
                    msg = _("You must at least set a background width.")
                    self.add_error('background_width_height', msg)
                    raise ValidationError(msg)
        return cleaned_data


class BootstrapJumbotronPlugin(BootstrapPluginBase):
    name = _("Jumbotron")
    model_mixins = (ContainerGridMixin, ImagePropertyMixin, ImageBackgroundMixin)
    require_parent = False
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    allow_children = True
    alien_child_classes = True
    form = JumbotronFormMixin
    raw_id_fields = ['image_file']
    render_template = 'cascade/bootstrap4/jumbotron.html'
    ring_plugin = 'JumbotronPlugin'
    footnote_html = """<p>
    For more information about the Jumbotron please read the
    <a href="https://getbootstrap.com/docs/4.3/components/jumbotron/" target="_new">Bootstrap documentation</a>.
    </p>"""

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/jumbotronplugin.js']

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        try:
            elements = get_picture_elements(instance)
        except Exception as exc:
            logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        else:
            try:
                if instance.child_plugin_instances and instance.child_plugin_instances[0].plugin_type == 'BootstrapRowPlugin':
                    padding='padding: {0}px {0}px;'.format(int(app_settings.CMSPLUGIN_CASCADE['bootstrap4']['gutter']/2))
                    context.update({'add_gutter_if_child_is_BootstrapRowPlugin': padding,})
                context.update({
                    'elements': [e for e in elements if 'media' in e] if elements else [],
                    'CSS_PREFIXES': app_settings.CSS_PREFIXES,
                })
            except Exception as exc:
                logger.warning("Unable generate picture elements. Reason: {}".format(exc))
        return self.super(BootstrapJumbotronPlugin, self).render(context, instance, placeholder)

    @classmethod
    def sanitize_model(cls, obj):
        sanitized = False
        super().sanitize_model(obj)
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
        identifier = super().get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = _("Without background image")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapJumbotronPlugin)
