# -*- coding: utf-8 -*-
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, PartialFormField
from cmsplugin_bootstrap.widgets import NumberInputWidget, MultipleNumberWidget, MultipleInlineStylesWidget


class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    default_css_class = 'carousel'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    render_template = 'cms/plugins/bootstrap/carousel.html'
    child_classes = ['TextPlugin', 'SlidePlugin']
    default_inline_styles = { 'overflow': 'hidden' }
    partial_fields = (
        PartialFormField('-num-children-',  # temporary field, not stored in the database
            NumberInputWidget(attrs={ 'style': 'width: 30px;' }),
            label=_('Number of Slides'), help_text=_('Number of slides for this carousel.')
        ),
        PartialFormField('options', MultipleNumberWidget(['interval', 'pause']),
            label=_('Carousel Options'), help_text=_('Interval and Pause settings.')
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
        wanted_children = int(obj.context['-num-children-'])
        super(CarouselPlugin, self).save_model(request, obj, form, change)
        self.extend_children(obj, wanted_children, SlidePlugin)

plugin_pool.register_plugin(CarouselPlugin)


class SlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    default_css_class = 'item'
    parent_classes = ['CarouselPlugin']
    require_parent = True
    child_classes = ['TextPlugin', 'FilerImagePlugin']

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(SlidePlugin, cls).get_css_classes(obj)
        if obj.get_previous_sibling() is None:
            css_classes.append('active')
        return css_classes

plugin_pool.register_plugin(SlidePlugin)
