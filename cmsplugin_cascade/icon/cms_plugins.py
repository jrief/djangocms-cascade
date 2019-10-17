from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.icon.forms import IconFormMixin
from cmsplugin_cascade.icon.plugin_base import IconPluginMixin


class SimpleIconPlugin(IconPluginMixin, LinkPluginBase):
    name = _("Simple Icon")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/simpleicon.html'
    form = type('SimpleIconForm', (LinkFormMixin, IconFormMixin), {'require_link': False})
    model_mixins = (LinkElementMixin,)
    ring_plugin = 'IconPlugin'

    class Media:
        js = ['cascade/js/admin/iconplugin.js']


    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(SimpleIconPlugin, cls).get_css_classes(obj)
        if cls.plugin_class.__class__ == 'BootstrapNavItemsPlugin':
            css_classes.insert(0,'nav-link navbar-text')
        return css_classes

plugin_pool.register_plugin(SimpleIconPlugin)

class TextIconPlugin(IconPluginMixin, LinkPluginBase):
    """
    This plugin is intended to be used inside the django-CMS-CKEditor.
    """
    name = _("Icon in text")
    text_enabled = True
    render_template = 'cascade/plugins/texticon.html'
    ring_plugin = 'IconPlugin'
    parent_classes = ['TextPlugin']
    form = type('TextIconForm', (LinkFormMixin, IconFormMixin), {'require_link': False})
    model_mixins = (LinkElementMixin,)
    allow_children = False
    require_parent = False

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

plugin_pool.register_plugin(TextIconPlugin)
