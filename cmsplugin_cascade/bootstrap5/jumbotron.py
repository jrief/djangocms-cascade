import logging

from django.core.exceptions import ValidationError
from django.forms import widgets, BooleanField, ChoiceField
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade import app_settings
# from cmsplugin_cascade.fields import ColorField, MultiSizeField, CascadeImageField
from cmsplugin_cascade.models import CascadeElement
# from cmsplugin_cascade.image import ImagePropertyMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.picture import ImageElementMixin
# from cmsplugin_cascade.bootstrap5.container import ContainerGridMixin
from cmsplugin_cascade.bootstrap5.fields import BootstrapMultiSizeField
# from cmsplugin_cascade.bootstrap5.picture import get_picture_elements

from finder.forms.fields import FinderFileField
from finder.models.file import FileModel as FinderFileModel

from formset.forms import ModelForm

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


class BackgroundChoiceWidget(widgets.RadioSelect):
    """
    Render sample backgrounds in different colors.
    """
    template_name = 'cascade/admin/widgets/background_choices.html'
    BACKGROUND_COLOR_CHOICES = [
        ('bg-body text-body', _("Body Standard")),
        ('bg-body-secondary', _("Body Secondary")),
        ('bg-body-tertiary', _("Body Tertiary")),
        ('bg-primary text-white', _("Primary")),
        ('bg-primary-subtle text-primary-emphasis', _("Subtle Primary")),
        ('bg-secondary', _("Secondary")),
        ('bg-secondary-subtle', _("Subtle Secondary")),
        ('bg-success text-white', _("Success")),
        ('bg-success-subtle text-success-emphasis', _("Subtle Success")),
        ('bg-danger text-white', _("Danger")),
        ('bg-danger-subtle text-danger-emphasis', _("Subtle Danger")),
        ('bg-warning text-dark', _("Warning")),
        ('bg-warning-subtle text-warning-emphasis', _("Subtle Warning")),
        ('bg-info text-dark', _("Info")),
        ('bg-info-subtle text-info-emphasis', _("Subtle Info")),
        ('bg-light text-dark', _("Light")),
        ('bg-light-subtle text-light-emphasis', _("Subtle Light")),
        ('bg-dark text-white', _("Dark")),
        ('bg-dark-subtle text-dark-emphasis', _("Subtle Dark")),
    ]

    def get_context(self, name, value, attrs):
        attrs = attrs or {}
        context = super().get_context(name, value, attrs)
        return context


class JumbotronForm(ModelForm):
    """
    Form class to validate the JumbotronPlugin.
    """
    ATTACHMENT_CHOICES = ['scroll', 'fixed', 'local']
    VERTICAL_POSITION_CHOICES = ['top', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'bottom']
    HORIZONTAL_POSITION_CHOICES = ['left', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'right']
    REPEAT_CHOICES = ['repeat', 'repeat-x', 'repeat-y', 'no-repeat']
    SIZE_CHOICES = ['auto', 'width/height', 'cover', 'contain']

    # BUTTON_STYLE_CHOICES = [
    #     ('btn-outline-success', _("Success")),
    #     ('btn-outline-danger', _("Danger")),
    #     ('btn-outline-warning', _("Warning")),
    #     ('btn-outline-info', _("Info")),
    #     ('btn-outline-light', _("Light")),
    #     ('btn-outline-dark', _("Dark")),
    #     ('btn-outline-link', _("Link")),
    # ]
    #
    # BUTTON_STYLE_CHOICES = [
    #     ('text-bg-light', _("Light with contrasting color")),
    #     ('text-bg-dark', _("Dark with contrasting color")),
    # ]

    # style = ChoiceField(
    #     label=_("Style"),
    #     choices=JUMBOTRON_STYLE_CHOICES,
    #     initial=JUMBOTRON_STYLE_CHOICES[0][0],
    # )

    fluid = BooleanField(
        label=_("Is fluid"),
        initial=True,
        required=False,
        help_text=_("Shall this element occupy the entire horizontal space of its parent."),
    )

    # element_heights = BootstrapMultiSizeField(
    #     label=("Element Heights"),
    #     required=True,
    #     allowed_units=['rem', 'px', 'auto'],
    #     initial='300px',
    #     help_text=_("This property specifies the height for each Bootstrap breakpoint."),
    # )

    background_color = ChoiceField(
        label=_("Background color"),
        choices=BackgroundChoiceWidget.BACKGROUND_COLOR_CHOICES,
        widget=BackgroundChoiceWidget(),
        initial=BackgroundChoiceWidget.BACKGROUND_COLOR_CHOICES[0][0],
    )
    image = FinderFileField(
        accept_mime_types=['image/*'],
        label=_("Background Image"),
        required=False,
    )
    background_repeat = ChoiceField(
        label=_("Background repeat"),
        choices=[(c, c) for c in REPEAT_CHOICES],
        widget=BackgroundChoiceWidget(attrs={'df-show': '.image'}),
        initial='no-repeat',
        required=False,
        help_text=_("This property specifies how the background image repeates."),
    )
    background_attachment = ChoiceField(
        label=_("Background attachment"),
        choices=[(c, c) for c in ATTACHMENT_CHOICES],
        widget=BackgroundChoiceWidget(attrs={'df-show': '.image'}),
        initial='local',
        required=False,
        help_text=_("This property specifies how to move the background image relative to the viewport."),
    )
    background_vertical_position = ChoiceField(
        label=_("Background vertical position"),
        choices=[(c, c) for c in VERTICAL_POSITION_CHOICES],
        widget=widgets.Select(attrs={'df-show': '.image'}),
        initial='center',
        required=False,
        help_text=_("This property moves a background image vertically within its container."),
    )
    background_horizontal_position = ChoiceField(
        label=_("Background horizontal position"),
        choices=[(c, c) for c in HORIZONTAL_POSITION_CHOICES],
        widget=widgets.Select(attrs={'df-show': '.image'}),
        initial='center',
        required=False,
        help_text=_("This property moves a background image horizontally within its container."),
    )
    background_size = ChoiceField(
        label=_("Background size"),
        choices=[(c, c) for c in SIZE_CHOICES],
        widget=widgets.Select(attrs={'df-show': '.image'}),
        initial='auto',
        required=False,
        help_text=_("This property specifies how the background image is sized."),
    )

    # background_width_height = MultiSizeField(
    #     ['width', 'height'],
    #     label=_("Background width/height"),
    #     sublabels=[_("Width"), _("Height")],
    #     allowed_units=['px', '%'],
    #     required=False,
    #     help_text=_("This property specifies the width and height of a background image in px or %."),
    # )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {
            'glossary': [
                'fluid', 'background_color', 'image', 'background_repeat',
                'background_attachment', 'background_vertical_position', 'background_horizontal_position',
                'background_size',
            ],
        }

    def validate_optional_field(self, name):
        field = self.fields[name]
        value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
        if value in field.empty_values:
            self.add_error(name, ValidationError(field.error_messages['required'], code='required'))
        else:
            return value

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['image']:
            self.validate_optional_field('background_repeat')
            self.validate_optional_field('background_attachment')
            self.validate_optional_field('background_vertical_position')
            self.validate_optional_field('background_horizontal_position')
            # if self.validate_optional_field('background_size') == 'width/height':
            #     try:
            #         cleaned_data['background_width_height']['width']
            #     except KeyError:
            #         msg = _("You must at least set a background width.")
            #         self.add_error('background_width_height', msg)
            #        raise ValidationError(msg)
        return cleaned_data


class BootstrapJumbotronPlugin(BootstrapPluginBase):
    name = _("Jumbotron")
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    default_css_class = 'p-3'
    # model_mixins = (ImagePropertyMixin, ImageBackgroundMixin)
    model_mixins = (ImageElementMixin, ImageBackgroundMixin)
    form = JumbotronForm
    render_template = 'cascade/bootstrap5/jumbotron.html'
    # footnote_html = ""

    class Media:
        css = {'all': [
            'cascade/css/background.css',
        ]}

    def render(self, context, instance, placeholder):
        # image shall be rendered in a responsive context using the ``<picture>`` element
        if instance.image:
            pass  # the background image
        return self.super(BootstrapJumbotronPlugin, self).render(context, instance, placeholder)

    # @classmethod
    # def sanitize_model(cls, obj):
    #     sanitized = False
    #     super().sanitize_model(obj)
    #     grid_container = obj.get_bound_plugin().get_grid_instance()
    #     obj.glossary.setdefault('media_queries', {})
    #     for bp, bound in grid_container.bounds.items():
    #         obj.glossary['media_queries'].setdefault(bp.name, {})
    #         width = round(bound.max)
    #         if obj.glossary['media_queries'][bp.name].get('width') != width:
    #             obj.glossary['media_queries'][bp.name]['width'] = width
    #             sanitized = True
    #         if obj.glossary['media_queries'][bp.name].get('media') != bp.media_query:
    #             obj.glossary['media_queries'][bp.name]['media'] = bp.media_query
    #             sanitized = True
    #     return sanitized

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapJumbotronPlugin, cls).get_css_classes(obj)
        if obj.glossary.get('style'):
            css_classes.append(obj.glossary.get('style'))
        if obj.glossary.get('fluid'):
            css_classes.append('w-100')
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = gettext("Without background image")
        return format_html('{0}{1}', identifier, content)

plugin_pool.register_plugin(BootstrapJumbotronPlugin)
