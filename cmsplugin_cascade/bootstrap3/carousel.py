# -*- coding: utf-8 -*-
import os
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms.fields import IntegerField
from django.forms.models import ModelForm
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.forms import ManageChildrenFormMixin
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleCascadingSizeWidget
from .plugin_base import BootstrapPluginBase
from .settings import CASCADE_BREAKPOINTS_LIST, CMS_CASCADE_TEMPLATE_DIR


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
    render_template = os.path.join('cms', CMS_CASCADE_TEMPLATE_DIR, 'carousel.html')
    default_inline_styles = {'overflow': 'hidden'}
    fields = ('num_children', 'glossary',)
    DEFAULT_CAROUSEL_ATTRIBUTES = {'data-ride': 'carousel'}
    OPTION_CHOICES = (('slide', _("Animate")), ('pause', _("Pause")), ('wrap', _("Wrap")),)
    GLOSSARY_FIELDS = (
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
    )

    def get_form(self, request, obj=None, **kwargs):
        self.glossary_fields = list(self.GLOSSARY_FIELDS)
        if obj:
            breakpoints = obj.get_complete_glossary().get('breakpoints', CASCADE_BREAKPOINTS_LIST)
            self.glossary_fields.append(PartialFormField('container_max_heights',
                MultipleCascadingSizeWidget(breakpoints),
                label=_("Carousel heights"),
                help_text=_("Heights of Carousel in pixels for distinct Bootstrap's breakpoints."),
            ))
        return super(CarouselPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)

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
        if obj:
            # fill all unset maximum heights for this container to meaningful values
            breakpoints = obj.get_complete_glossary().get('breakpoints', CASCADE_BREAKPOINTS_LIST)
            max_height = max(obj.glossary['container_max_heights'].values())
            for bp in breakpoints:
                if not obj.glossary['container_max_heights'][bp]:
                    obj.glossary['container_max_heights'][bp] = max_height
        super(CarouselPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, CarouselSlidePlugin)

plugin_pool.register_plugin(CarouselPlugin)


class CarouselSlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    default_css_class = 'item'
    parent_classes = ['CarouselPlugin']
    change_form_template = 'cms/admin/change_form-empty.html'

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(CarouselSlidePlugin, cls).get_css_classes(obj)
        if obj.get_previous_sibling() is None:
            css_classes.append('active')
        return css_classes

plugin_pool.register_plugin(CarouselSlidePlugin)
