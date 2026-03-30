import logging

from django.forms import widgets
from django.forms.fields import IntegerField, MultipleChoiceField, BooleanField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _, ngettext

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.bootstrap5.breakpoint import Breakpoint
from cmsplugin_cascade.bootstrap5.fields import AspectRatioChoiceField
from cmsplugin_cascade.bootstrap5.mixins import AspectRatioChoicesMixin, VerticalMarginsMixin
from cmsplugin_cascade.bootstrap5.picture import LazySizesPictureMixin, ImageElementMixin
from cmsplugin_cascade.bootstrap5.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.bootstrap5.richtext import HyperlinkDialogForm
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.mixins import ManageChildrenMixin
from cmsplugin_cascade.models import CascadeElement
from cmsplugin_cascade.widgets import NumberInputWidget

from finder.forms.fields import FinderFileField
from formset.forms import ModelForm
from formset.formfields.richtext import RichTextarea, RichTextField
from formset.richtext import controls

logger = logging.getLogger('cascade')


class CarouselSlidesForm(ManageChildrenFormMixin, ModelForm):
    OPTION_CHOICES = [
        ('fade', _("Fade transition")),
        ('wrap', _("Wrap")),
        ('ride', _("Autoplays")),
        ('pause', _("Pause on hover")),
    ]

    num_children = IntegerField(
        label=_("Items"),
        min_value=1,
        initial=1,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        help_text=_("Number of slides for this carousel."),
    )
    aspect_ratio = AspectRatioChoiceField(Breakpoint.xs)
    interval = IntegerField(
        label=_("Interval"),
        min_value=1,
        initial=5,
        widget=NumberInputWidget(attrs={'size': '3', 'style': 'width: 5em !important;'}),
        help_text=_("Change slide after this number of seconds."),
    )
    options = MultipleChoiceField(
        label=_("Options"),
        choices=OPTION_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        initial=['wrap'],
        required=False,
        help_text=_("Set options for this Carousel."),
    )
    add_controls = BooleanField(
        label=_("Add controls"),
        required=False,
        initial=True,
    )
    add_indicators = BooleanField(
        label=_("Add indicators"),
        required=False,
        initial=True,
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['aspect_ratio', 'interval', 'options', 'add_controls', 'add_indicators']}


class BootstrapCarouselPlugin(ManageChildrenMixin, VerticalMarginsMixin, AspectRatioChoicesMixin, BootstrapPluginBase):
    name = _("Carousel")
    default_css_class = 'carousel slide'
    parent_classes = ['BootstrapColumnPlugin']
    direct_child_classes = child_classes = ['BootstrapCarouselSlidePlugin']
    render_template = 'cascade/bootstrap5/{}carousel.html'
    default_inline_styles = {'overflow': 'hidden'}
    form = CarouselSlidesForm
    DEFAULT_CAROUSEL_ATTRIBUTES = {'data-ride': 'carousel'}

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_num_children()
        content = ngettext('with {0} slide', 'with {0} slides', num_cols).format(num_cols)
        return mark_safe(content)

    @classmethod
    def get_css_classes(cls, instance):
        css_classes = cls.super(BootstrapCarouselPlugin, cls).get_css_classes(instance)
        options = instance.glossary.get('options', [])
        if 'fade' in options:
            css_classes.append('carousel-fade')
        return css_classes

    @classmethod
    def get_html_tag_attributes(cls, instance):
        attributes = cls.super(BootstrapCarouselPlugin, cls).get_html_tag_attributes(instance)
        attributes.update(cls.DEFAULT_CAROUSEL_ATTRIBUTES)
        options = instance.glossary.get('options', [])
        attributes['data-bs-pause'] = 'pause' in options and 'hover' or 'false'
        attributes['data-bs-ride'] = 'ride' in options and 'carousel' or 'false'
        attributes['data-bs-wrap'] = 'wrap' in options and 'true' or 'false'
        return attributes

    def render(self, context, instance, placeholder):
        context = self.super(BootstrapCarouselPlugin, self).render(context, instance, placeholder)
        context['show_controls'] = instance.glossary.get('add_controls', True)
        context['show_indicators'] = instance.glossary.get('add_indicators', True)
        return context

    def save_model(self, request, instance, form, change):
        wanted_children = int(form.cleaned_data.get('num_children'))
        super().save_model(request, instance, form, change)
        self.extend_children(instance, wanted_children, BootstrapCarouselSlidePlugin)
        keys = ['aspect_ratio' if bp == 'xs' else f'aspect_ratio_{bp}' for bp in self.get_breakpoints(instance)]
        if any(key in form.changed_data for key in keys):
            for model in CascadeElement._get_cascade_elements():
                # execute query to not iterate over SELECT ... FROM while updating other models
                children = list(model.objects.filter(parent_id=instance.id))
                for child in children:
                    child.glossary.pop('cached_sources', None)
                    child.save(update_fields=['glossary'])


plugin_pool.register_plugin(BootstrapCarouselPlugin)


class BootstrapSlideForm(ModelForm):
    image = FinderFileField(
        accept_mime_types=['image/*'],
        label=_("Image"),
    )
    caption = RichTextField(
        label=_("Caption"),
        widget=RichTextarea(
            control_elements=[
                controls.Heading(),
                controls.Bold(),
                controls.Italic(),
                controls.DialogControl(
                    HyperlinkDialogForm(),
                    icon='formset/icons/link.svg',
                ),
                controls.ClearFormat(),
            ],
        )
    )

    class Meta:
        model = CascadeElement
        exclude = ['shared_glossary']
        fields_map = {'glossary': ['image', 'caption']}


class BootstrapCarouselSlidePlugin(LazySizesPictureMixin, BootstrapPluginBase):
    name = _("Carousel Slide")
    model_mixins = (ImageElementMixin,)
    default_css_class = 'img-fluid'
    direct_parent_classes = parent_classes = ['BootstrapCarouselPlugin']
    child_classes = []
    allow_children = False
    html_tag_attributes = {'image_title': 'title', 'alt_tag': 'tag'}
    render_template = 'cascade/bootstrap5/carousel-slide.html'
    default_css_class = 'lazyload text-bg-light w-100'
    form = BootstrapSlideForm

    @classmethod
    def get_identifier(cls, obj):
        try:
            content = obj.image.name or obj.image.original_filename
        except AttributeError:
            content = gettext("Empty Slide")
        return mark_safe(content)

    @classmethod
    def get_html_tag_attributes(cls, instance):
        attributes = cls.super(BootstrapCarouselSlidePlugin, cls).get_html_tag_attributes(instance)
        parent_glossary = instance.get_parent_glossary()
        attributes['data-bs-interval'] = 1000 * int(parent_glossary.get('interval', 5))
        return attributes

    def render(self, context, instance, placeholder):
        if not (sources := instance.glossary.get('cached_sources')):
            if instance.image:
                allowed_breakpoints = self.get_breakpoints(instance)
                parent_glossary = instance.get_parent_glossary()
                for bp in allowed_breakpoints:
                    key = 'aspect_ratio' if bp == 'xs' else f'aspect_ratio_{bp}'
                    instance.glossary[key] = parent_glossary.get(key, '')
                sources = self.get_picture_sources(instance)
                instance.glossary['cached_sources'] = sources
                instance.save(update_fields=['glossary'])

        context = self.super(BootstrapCarouselSlidePlugin, self).render(context, instance, placeholder)
        if instance.image:
            if not (alt_text := instance.image.meta_data.get(f'alt_text_{instance.language}')):
                alt_text = instance.image.meta_data.get('alt_text', instance.image.name)
        else:
            alt_text = ""
        context.update({
            'picture': {'sources': sources, 'fallback_image': self.fallback_image, 'alt': alt_text},
            'caption': instance.glossary.get('caption', ''),
        })
        return context

    def save_model(self, request, obj, form, change):
        obj.glossary.pop('cached_sources', None)
        return super().save_model(request, obj, form, change)

plugin_pool.register_plugin(BootstrapCarouselSlidePlugin)
