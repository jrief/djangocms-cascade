from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin
from entangled.forms import EntangledModelFormMixin


class TextLinkFormMixin(EntangledModelFormMixin):
    link_content = CharField(
        label=_("Link Content"),
        widget=TextInput(attrs={'id': 'id_name'}),  # replace auto-generated id so that CKEditor automatically transfers the text into this input field
        help_text=_("Content of Link"),
    )

    class Meta:
        entangled_fields = {'glossary': ['link_content']}


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    model_mixins = (LinkElementMixin,)
    text_enabled = True
    render_template = 'cascade/link/text-link.html'
    ring_plugin = 'TextLinkPlugin'
    form = TextLinkFormMixin
    parent_classes = ['TextPlugin']

    class Media:
        js = ['cascade/js/admin/textlinkplugin.js']


    @classmethod
    def get_css_classes(cls, obj):
        css_classes = cls.super(TextLinkPlugin, cls).get_css_classes(obj)
        if obj.parent.plugin_type == 'TextPlugin' and obj.parent.parent.plugin_type == 'BootstrapListsPlugin' :
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
