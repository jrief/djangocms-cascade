# -*- coding: utf-8 -*-
import os
from django.forms import widgets
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.widgets import NumberInputWidget, MultipleTextInputWidget, MultipleInlineStylesWidget
from .plugin_base import BootstrapPluginBase
from . import settings


class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    default_css_class = 'carousel'
    default_css_attributes = ('options',)
    parent_classes = ['BootstrapColumnPlugin']
    render_template = os.path.join('cms', settings.CMS_CASCADE_TEMPLATE_DIR, 'carousel.html')
    default_inline_styles = {'overflow': 'hidden'}
    default_data_options = {'ride': 'carousel'}
    glossary_fields = (
        PartialFormField('-num-children-',  # temporary field, not stored in the database
            NumberInputWidget(attrs={'size': '2'}),
            label=_('Number of Slides'), help_text=_('Number of slides for this carousel.')
        ),
        PartialFormField('data_options', MultipleTextInputWidget(['interval', 'pause']),
            label=_('Carousel Options'), help_text=_('Adjust interval and pause for the carousel.')
        ),
        PartialFormField('options',
            widgets.CheckboxSelectMultiple(choices=(('slide', _('Animate')),)),
                label=_('Options'),
        ),
        PartialFormField('inline_styles', MultipleInlineStylesWidget(['height']),
            label=_('Inline Styles'), help_text=_('Height of carousel.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        num_cols = obj.get_children().count()
        return ungettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)

    def save_model(self, request, obj, form, change):
        wanted_children = int(obj.glossary['-num-children-'])
        super(CarouselPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, SlidePlugin)

plugin_pool.register_plugin(CarouselPlugin)


class SlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    default_css_class = 'item'
    parent_classes = ['CarouselPlugin']
    generic_child_classes = settings.CMS_CASCADE_LEAF_PLUGINS

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(SlidePlugin, cls).get_css_classes(obj)
        if obj.get_previous_sibling() is None:
            css_classes.append('active')
        return css_classes

plugin_pool.register_plugin(SlidePlugin)
