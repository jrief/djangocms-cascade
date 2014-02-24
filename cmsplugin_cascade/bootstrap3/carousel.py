# -*- coding: utf-8 -*-
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import PartialFormField
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleTextInputWidget, MultipleInlineStylesWidget
from cmsplugin_cascade.bootstrap3.plugin_base import BootstrapPluginBase


class CheckboxInputWidget(widgets.CheckboxInput):
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='checkbox', name=name)
        if self.check_test(value):
            final_attrs['checked'] = 'checked'
        if not (value is True or value is False or value is None or value == '' or value == 'False' or value == 'None'):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(value)
        return format_html('<input{0} />', flatatt(final_attrs))

    @classmethod
    def is_true(self, value):
        return not (value is False or value is None or value == 'False' or value == 'None' or value == '')


class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    default_css_class = 'carousel'
    parent_classes = ['BootstrapColumnPlugin']
    render_template = 'cms/bootstrap3/carousel.html'
    default_inline_styles = { 'overflow': 'hidden' }
    default_data_options = { 'ride': 'carousel' }
    partial_fields = (
        PartialFormField('-num-children-',  # temporary field, not stored in the database
            NumberInputWidget(attrs={ 'size': '2' }),
            label=_('Number of Slides'), help_text=_('Number of slides for this carousel.')
        ),
        PartialFormField('data_options', MultipleTextInputWidget(['interval', 'pause']),
            label=_('Carousel Options'), help_text=_('Adjust interval and pause for the carousel.')
        ),
        PartialFormField('data_animate', CheckboxInputWidget(check_test=CheckboxInputWidget.is_true),
            label=_('Carousel Animate'), help_text=_('Animate the carousel')
        ),
        PartialFormField('inline_styles', MultipleInlineStylesWidget(['height']),
            label=_('Inline Styles'), help_text=_('Height of carousel.')
        ),
    )

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(CarouselPlugin, cls).get_css_classes(obj)
        val = obj.context.get('data_animate')
        if CheckboxInputWidget.is_true(val):
            css_classes.append('slide')
        return css_classes

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)

    def save_model(self, request, obj, form, change):
        wanted_children = int(obj.context['-num-children-'])
        super(CarouselPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, SlidePlugin)

plugin_pool.register_plugin(CarouselPlugin)


class SlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    default_css_class = 'item'
    parent_classes = ['CarouselPlugin']
    generic_child_classes = ('TextPlugin', 'FilerImagePlugin',)

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(SlidePlugin, cls).get_css_classes(obj)
        if obj.get_previous_sibling() is None:
            css_classes.append('active')
        return css_classes

plugin_pool.register_plugin(SlidePlugin)
