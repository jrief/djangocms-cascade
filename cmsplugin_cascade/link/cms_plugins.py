from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.forms import TextLinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    model_mixins = (LinkElementMixin,)
    text_enabled = True
    render_template = 'cascade/link/text-link.html'
    ring_plugin = 'TextLinkPlugin'
    form = type('TextLinkForm', (LinkFormMixin, TextLinkFormMixin), {})
    parent_classes = ['TextPlugin']

    class Media:
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/textlinkplugin.js']


    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(TextLinkPlugin, cls).get_css_classes(obj)
        if hasattr(obj.parent.parent, 'plugin_type' ) and obj.parent.parent.plugin_type == 'BootstrapListsPlugin':
            css_classes.insert(0,'nav-link navbar-text')
        # strides pass
        if hasattr(obj.parent.parent, 'plugin'):
            css_classes.insert(0,'nav-link navbar-text')
        return css_classes


    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('link_content', ''))

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        """
        Workaround for `PluginPool.get_all_plugins()`, otherwise TextLinkPlugin is not allowed
        as a child of a `TextPlugin`.
        """
        return False

plugin_pool.register_plugin(TextLinkPlugin)
