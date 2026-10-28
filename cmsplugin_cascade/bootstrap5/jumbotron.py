import logging

from django.core.exceptions import ValidationError
from django.forms import widgets, CharField, ChoiceField
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.bootstrap5.fields import AspectRatioChoiceField
from cmsplugin_cascade.bootstrap5.mixins import AspectRatioChoicesMixin, PaddingsMixin, VerticalMarginsMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.picture import ImageElementMixin, LazySizesPictureMixin
from cmsplugin_cascade.forms import InternalTitleModelForm

from finder.forms.fields import FinderFileField

from formset.forms import ModelForm

logger = logging.getLogger('cascade')


class ImageBackgroundMixin:
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


class BorderColorWidget(widgets.RadioSelect):
    """
    Render sample border colors in different colors.
    """
    template_name = 'cascade/admin/widgets/background_choices.html'
    BORDER_COLOR_CHOICES = [
        ('', _("No border")),
        ('border-primary', _("Primary")),
        ('border-primary-subtle', _("Subtle Primary")),
        ('border-secondary', _("Secondary")),
        ('border-secondary-subtle', _("Subtle Secondary")),
        ('border-success', _("Success")),
        ('border-success-subtle', _("Subtle Success")),
        ('border-danger', _("Danger")),
        ('border-danger-subtle', _("Subtle Danger")),
        ('border-warning', _("Warning")),
        ('border-warning-subtle', _("Subtle Warning")),
        ('border-info', _("Info")),
        ('border-info-subtle', _("Subtle Info")),
        ('border-light', _("Light")),
        ('border-light-subtle', _("Subtle Light")),
        ('border-dark', _("Dark")),
        ('border-dark-subtle', _("Subtle Dark")),
        ('border-white', _("White")),
        ('border-black', _("Black")),
    ]


class BorderWidthWidget(widgets.RadioSelect):
    """
    Render sample border widths in different widths.
    """
    template_name = 'cascade/admin/widgets/background_choices.html'
    BORDER_WIDTH_CHOICES = [
        ('border-1', _("1 pixel")),
        ('border-2', _("2 pixels")),
        ('border-3', _("3 pixels")),
        ('border-4', _("4 pixels")),
        ('border-5', _("5 pixels")),
    ]


class RoundedCornerWidget(widgets.RadioSelect):
    template_name = 'cascade/admin/widgets/background_choices.html'
    ROUNDED_CHOICES = [
        ('rounded-0', _("Unrounded Corner")),
        ('rounded-1', _("Rounded 4 pixel")),
        ('rounded-2', _("Rounded 6 pixels")),
        ('rounded-3', _("Rounded 8 pixels")),
        ('rounded-4', _("Rounded 16 pixels")),
        ('rounded-5', _("Rounded 32 pixels")),
        ('rounded-circle', _("Rounded Circle")),
        ('rounded-pill', _("Rounded Pill")),
    ]


class JumbotronForm(InternalTitleModelForm):
    """
    Form class to validate the JumbotronPlugin.
    """
    ATTACHMENT_CHOICES = ['scroll', 'fixed', 'local']
    VERTICAL_POSITION_CHOICES = ['top', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'bottom']
    HORIZONTAL_POSITION_CHOICES = ['left', '10%', '20%', '30%', '40%', 'center', '60%', '70%', '80%', '90%', 'right']
    REPEAT_CHOICES = ['repeat', 'repeat-x', 'repeat-y', 'no-repeat']
    SIZE_CHOICES = ['auto', 'width/height', 'cover', 'contain']
    background_color = ChoiceField(
        label=_("Background color"),
        choices=BackgroundChoiceWidget.BACKGROUND_COLOR_CHOICES,
        widget=BackgroundChoiceWidget(),
        initial=BackgroundChoiceWidget.BACKGROUND_COLOR_CHOICES[0][0],
    )
    border_color = ChoiceField(
        label=_("Border color"),
        choices=BorderColorWidget.BORDER_COLOR_CHOICES,
        widget=BorderColorWidget(),
        initial=BorderColorWidget.BORDER_COLOR_CHOICES[0][0],
        required=False,
        help_text=_("This property specifies the border color."),
    )
    border_width = ChoiceField(
        label=_("Border width"),
        choices=BorderWidthWidget.BORDER_WIDTH_CHOICES,
        widget=BorderWidthWidget(attrs={'df-show': '.border_color'}),
        initial=BorderWidthWidget.BORDER_WIDTH_CHOICES[0][0],
        required=False,
        help_text=_("This property specifies the border width."),
    )
    rounded_corder = ChoiceField(
        label=_("Rounded corners"),
        choices=RoundedCornerWidget.ROUNDED_CHOICES,
        widget=RoundedCornerWidget(),
        initial=RoundedCornerWidget.ROUNDED_CHOICES[3][0],
        required=False,
        help_text=_("This property specifies corner rounding."),
    )
    image = FinderFileField(
        accept_mime_types=['image/*'],
        label=_("Background Image"),
        required=False,
    )
    aspect_ratio = AspectRatioChoiceField(
        Breakpoint.xs,
        label=_("Aspect Ratio for Image"),
        widget=widgets.Select(attrs={'df-show': '.image'}),
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

    class Meta(InternalTitleModelForm.Meta):
        fields_map = {
            'glossary': [
                'title_attribute', 'background_color', 'border_color', 'border_width', 'rounded_corder', 'image',
                'aspect_ratio', 'background_repeat', 'background_attachment', 'background_vertical_position',
                'background_horizontal_position', 'background_size',
            ],
        }

    def clean(self):
        def validate_optional_field(name):
            field = self.fields[name]
            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            if value in field.empty_values:
                self.add_error(name, ValidationError(field.error_messages['required'], code='required'))
            else:
                return value

        cleaned_data = super().clean()
        if cleaned_data['image']:
            validate_optional_field('background_repeat')
            validate_optional_field('background_attachment')
            validate_optional_field('background_vertical_position')
            validate_optional_field('background_horizontal_position')
        return cleaned_data

    def full_clean(self):
        super().full_clean()
        if 'image' in self.changed_data or 'aspect_ratio' in self.changed_data:
            self.instance.glossary.pop('cached_sources', None)


class BootstrapJumbotronPlugin(AspectRatioChoicesMixin, LazySizesPictureMixin, PaddingsMixin, VerticalMarginsMixin, BootstrapPluginBase):
    name = _("Jumbotron")
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    default_css_class = None
    model_mixins = (ImageElementMixin, ImageBackgroundMixin)
    form = JumbotronForm
    render_template = 'cascade/bootstrap5/jumbotron.html'
    footnote_html = ""

    class Media:
        css = {'all': [
            'cascade/css/admin/background.css',
        ]}

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(BootstrapJumbotronPlugin, cls).get_css_classes(obj)
        if background_color := obj.glossary.get('background_color'):
            css_classes.append(background_color)
        if border_color := obj.glossary.get('border_color'):
            css_classes.extend(['border', border_color])
            if border_width := obj.glossary.get('border_width'):
                css_classes.append(border_width)
        if rounded_corder := obj.glossary.get('rounded_corder'):
            css_classes.extend(['rounded', rounded_corder])
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        identifier = super().get_identifier(obj)
        try:
            content = obj.title_attribute or obj.image.name or obj.image.original_filename
        except AttributeError:
            content = gettext("Without background image")
        return format_html('{0}{1}', identifier, content)

    def render(self, context, instance, placeholder):
        if instance.image:
            if cached_sources := instance.glossary.get('cached_sources'):
                context['image_sets'] = cached_sources
            else:
                ambit = instance.image.folder.get_ambit()
                sources = self.get_sources_bounds(instance)
                for source in sources:
                    # create images for image-set()
                    if source['min_width'] and source['max_width']:
                        source['media'] = '(min-width: {min_width}) and (max-width: {max_width})'.format(**source)
                    elif source['min_width']:
                        source['media'] = '(min-width: {min_width})'.format(**source)
                    elif source['max_width']:
                        source['media'] = '(max-width: {max_width})'.format(**source)
                    image_width = source['upper_bound']['width']
                    image_height = source['upper_bound']['height']
                    image_path, created = self.get_or_create_cropped(ambit, instance.image, image_width, image_height)
                    source['url_2x'] = ambit.sample_storage.url(image_path)
                    image_width, image_height = image_width / 2, image_height / 2
                    image_path, created = self.get_or_create_cropped(ambit, instance.image, image_width, image_height)
                    source['url_1x'] = ambit.sample_storage.url(image_path)
                context['image_sets'] = instance.glossary['cached_sources'] = sources
                instance.save(update_fields=['glossary'])

        return self.super(BootstrapJumbotronPlugin, self).render(context, instance, placeholder)


plugin_pool.register_plugin(BootstrapJumbotronPlugin)
