from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.config import LinkPluginBase, LinkFormMixin
from cmsplugin_cascade.link.plugin_base import LinkElementMixin
from cmsplugin_cascade.icon.forms import IconFormMixin
from cmsplugin_cascade.icon.plugin_base import IconPluginMixin
from django.forms.fields import CharField
from entangled.forms import EntangledModelFormMixin


class SimpleIconFormMixin(EntangledModelFormMixin):
    content = CharField(
        label=_('Content'),
        required=False,
        help_text=_("Content inside SimpleIcon"),
    )

    class Meta:
        entangled_fields = {'glossary': ['content']}


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
        js = ['admin/js/jquery.init.js', 'cascade/js/admin/iconplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

plugin_pool.register_plugin(TextIconPlugin)
