from django.utils.translation import gettext_lazy as _

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
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/iconplugin.js']

plugin_pool.register_plugin(SimpleIconPlugin)

