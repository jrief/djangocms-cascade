# -*- coding: utf-8 -*-
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from django.forms import widgets
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, PartialFormField
from cmsplugin_bootstrap.widgets import NumberInputWidget, MultipleNumberWidget, MultipleInlineStylesWidget


# class CarouselPlugin(BootstrapPluginBase):
#     name = _("Carousel")
#     parent_classes = ['BootstrapColumnPlugin']
#     require_parent = True
#     render_template = 'cms/plugins/bootstrap/carousel.html'
#     child_classes = ['SlidePlugin', 'TextPlugin']
#     #default_inline_styles = { 'overflow': 'hidden' }
#     partial_fields = (
#         PartialFormField('-num-children-',  # temporary field, not stored in the database
#             NumberInputWidget(),
#             label=_('Number of Slides'), help_text=_('Number of slides to be created with this carousel.')
#         ),
#         PartialFormField('options', MultipleNumberWidget(['interval', 'pause']),
#             label=_('Carousel Options'), help_text=_('Interval and Pause settings.')
#         ),
#         PartialFormField('inline_styles', MultipleInlineStylesWidget(['height']),
#             label=_('Inline Styles'), help_text=_('Height of carousel.')
#         ),
#     )
# 
#     @classmethod
#     def get_identifier(cls, obj):
#         num_cols = obj.get_children().count()
#         return ungettext_lazy('with {0} slide', 'with {0} slides', num_cols).format(num_cols)
# 
#     def save_model(self, request, obj, form, change):
#         wanted_children = int(obj.context['-num-children-'])
#         super(CarouselPlugin, self).save_model(request, obj, form, change)
#         self.extend_children(obj, wanted_children, SlidePlugin)

class CarouselPlugin(BootstrapPluginBase):
    name = _("Carousel")
    default_css_class = 'row'
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    child_classes = ['TextPlugin', 'SlidePlugin']
    partial_fields = (
        PartialFormField('-num-children-',  # temporary field, not stored in the database
            widgets.Select(choices=tuple((i, ungettext_lazy('{0} column', '{0} columns', i).format(i)) for i in range(1, 13))),
            label=_('Number of Columns'), help_text=_('Number of columns to be created with this row.')
        ),
        PartialFormField('inline_styles', MultipleInlineStylesWidget(['min-height']),
            label=_('Inline Styles'), help_text=_('Minimum height for this row.')
        ),
    )

plugin_pool.register_plugin(CarouselPlugin)


class SlidePlugin(BootstrapPluginBase):
    name = _("Slide")
    #render_template = 'cms/plugins/bootstrap/carousel-item.html'
    parent_classes = ['CarouselPlugin', 'SimpleWrapperPlugin']
    require_parent = True
    child_classes = ['TextPlugin', 'FilerImagePlugin']
    default_css_class = 'item'

    @classmethod
    def get_identifier(cls, obj):
        return u''

plugin_pool.register_plugin(SlidePlugin)
