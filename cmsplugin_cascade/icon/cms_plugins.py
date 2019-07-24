from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin
from cmsplugin_cascade.icon.mixins import IconPluginMixin


class SimpleIconPlugin(IconPluginMixin, LinkPluginBase):
    name = _("Simple Icon")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/simpleicon.html'
    model_mixins = (LinkElementMixin,)
    ring_plugin = 'IconPlugin'
    link_required = False

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

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
    model_mixins = (LinkElementMixin,)
    allow_children = False
    require_parent = False
    link_required = False

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

plugin_pool.register_plugin(TextIconPlugin)
