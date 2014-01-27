# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase, PartialFormField
from cmsplugin_bootstrap.widgets import MultipleInlineStylesWidget


class SimpleWrapperPlugin(BootstrapPluginBase):
    name = _("Simple Wrapper")
    parent_classes = ['BootstrapColumnPlugin']
    require_parent = True
    CLASS_CHOICES = ('thumbnail', 'jumbotron',)
    partial_fields = [
        PartialFormField('extra-bs-classes',
            widgets.Select(choices=tuple((cls, cls) for cls in CLASS_CHOICES)),
            label=_('Extra Bootstrap Classes'),
            help_text=_('Main Bootstrap CSS class to be added to this element.')
        ),
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(),
            label=_('Inline Styles'),
            help_text=_('Margins and minimum height for container.')
        )
    ]

plugin_pool.register_plugin(SimpleWrapperPlugin)


class HorizontalRulePlugin(BootstrapPluginBase):
    name = _("Horizontal Rule")
    require_parent = False
    allow_children = False
    tag_type = 'hr'
    render_template = 'cms/plugins/bootstrap/single.html'

plugin_pool.register_plugin(HorizontalRulePlugin)


class BootstrapThumbnailsPlugin(BootstrapPluginBase):
    name = _("Thumbnails")
    child_classes = ['BootstrapThumbImagePlugin']
    tag_type = 'ul'
    css_class_choices = (('thumbnails', 'thumbnails'),)

plugin_pool.register_plugin(BootstrapThumbnailsPlugin)


class BootstrapThumbImagePlugin(BootstrapPluginBase):
    name = _("Single thumbnail")
    parent_classes = ['BootstrapThumbnailsPlugin']
    require_parent = True
    tag_type = 'li'
    css_class_choices = (('thumbnail', 'thumbnail'),)

plugin_pool.register_plugin(BootstrapThumbImagePlugin)
