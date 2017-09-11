# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from cms.plugin_pool import plugin_pool

from .config import LinkPluginBase, LinkElementMixin, LinkForm
from .forms import TextLinkFormMixin


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    model_mixins = (LinkElementMixin,)
    text_enabled = True
    render_template = 'cascade/link/text-link.html'
    ring_plugin = 'TextLinkPlugin'
    fields = ('link_content',) + LinkPluginBase.fields
    parent_classes = ('TextPlugin',)

    class Media:
        js = ['cascade/js/admin/textlinkplugin.js']

    @classmethod
    def get_identifier(cls, obj):
        return mark_safe(obj.glossary.get('link_content', ''))

    def get_form(self, request, obj=None, **kwargs):
        link_content = CharField(required=True, label=_("Link Content"),
            # replace auto-generated id so that CKEditor automatically transfers the text into this input field
            widget=TextInput(attrs={'id': 'id_name'}), help_text=_("Content of Link"))
        Form = type(str('TextLinkForm'), (TextLinkFormMixin, LinkForm.get_form_class(),),  # @UndefinedVariable
            {'link_content': link_content})
        kwargs.update(form=Form)
        return super(TextLinkPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        """
        Workaround for `PluginPool.get_all_plugins()`, otherwise TextLinkPlugin is not allowed
        as a child of a `TextPlugin`.
        """
        return False

plugin_pool.register_plugin(TextLinkPlugin)
