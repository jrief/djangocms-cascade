# -*- coding: utf-8 -*-
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.plugin_base import PartialFormField
from cmsplugin_cascade.widgets import MultipleInlineStylesWidget
from cmsplugin_cascade.bootstrap3 import settings
from cmsplugin_cascade.bootstrap3.plugin_base import BootstrapPluginBase
from cmsplugin_cascade.cms_plugins import framework


class SimpleWrapperPlugin(BootstrapPluginBase):
    name = _("Simple Wrapper")
    parent_classes = ['BootstrapColumnPlugin']
    try:
        generic_child_classes = settings.CMS_CASCADE_LEAF_PLUGINS[framework]['SimpleWrapperPlugin']
    except KeyError:
        generic_child_classes = settings.CMS_CASCADE_LEAF_PLUGINS.get('default')
    CLASS_CHOICES = ((('', _('Unstyled')),) + tuple((cls, cls.title()) for cls in ('thumbnail', 'jumbotron',)))
    partial_fields = (
        PartialFormField('css_class',
            widgets.Select(choices=CLASS_CHOICES),
            label=_('Extra Bootstrap Classes'),
            help_text=_('Main Bootstrap CSS class to be added to this element.')
        ),
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['min-height']),
            label=_('Inline Styles'),
            help_text=_('Margins and minimum height for container.')
        ),
    )

    @classmethod
    def get_identifier(cls, obj):
        name = obj.context.get('css_class').title() or cls.CLASS_CHOICES[0][1]
        return name.title()

    @classmethod
    def get_css_classes(cls, obj):
        css_classes = super(SimpleWrapperPlugin, cls).get_css_classes(obj)
        css_class = obj.context.get('css_class')
        if css_class:
            css_classes.append(css_class)
        return css_classes

plugin_pool.register_plugin(SimpleWrapperPlugin)


class HorizontalRulePlugin(BootstrapPluginBase):
    name = _("Horizontal Rule")
    parent_classes = ['BootstrapContainerPlugin', 'BootstrapColumnPlugin']
    allow_children = False
    tag_type = 'hr'
    render_template = 'cms/plugins/single.html'
    partial_fields = (
        PartialFormField('inline_styles',
            MultipleInlineStylesWidget(['margin-top', 'margin-bottom']),
            label=_('Inline Styles'),
            help_text=_('Margins for this horizontal rule.')
        ),
    )

plugin_pool.register_plugin(HorizontalRulePlugin)
