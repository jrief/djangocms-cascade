# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.forms import widgets
from django.forms.fields import CharField
from django.forms.widgets import TextInput
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from cmsplugin_cascade.fields import GlossaryField
from cms.plugin_pool import plugin_pool

from .config import LinkPluginBase, LinkElementMixin, LinkForm
from .forms import TextLinkFormMixin

if 'cmsplugin_cascade.icon' in settings.INSTALLED_APPS:
    from cmsplugin_cascade.icon.mixins import IconPluginMixin
else:
    from cmsplugin_cascade.plugin_base import CascadePluginMixinBase as IconPluginMixin


class TextLinkIconMixin(IconPluginMixin):
    require_parent = True
    parent_classes = ('BootstrapColumnPlugin', 'SimpleWrapperPlugin',)
    render_template = 'cascade/link/text-link.html'
    allow_children = False
    ring_plugin = 'ButtonMixin'

    icon_align = GlossaryField(
        widgets.RadioSelect(choices=(('', _("No Icon")), ('icon-left', _("Icon placed left")),
                                     ('icon-right', _("Icon placed right")),)),
        label=_("Icon alignment"),
        initial='',
        help_text=_("Add an Icon before or after the button content.")
    )

    icon_font = GlossaryField(
        widgets.Select(),
        label=_("Font"),
    )

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    class Media:
        js = ['cascade/js/admin/buttonmixin.js']

    def render(self, context, instance, placeholder):
        context = super(TextLinkIconMixin, self).render(context, instance, placeholder)
        try:
            icon_font = self.get_icon_font(instance)
            symbol = instance.glossary.get('symbol')
        except AttributeError:
            icon_font, symbol = None, None
        if icon_font and symbol:
            context['stylesheet_url'] = icon_font.get_stylesheet_url()
            mini_template = '{0}<i class="icon-{1} {2}" aria-hidden="true"></i>{3}'
            icon_align = instance.glossary.get('icon_align')
            if icon_align == 'icon-left':
                context['icon_left'] = format_html(mini_template, '', symbol, 'cascade-icon-left', ' ')
            elif icon_align == 'icon-right':
                context['icon_right'] = format_html(mini_template, ' ', symbol, 'cascade-icon-right', '')
            print(context)
        return context


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    model_mixins = (LinkElementMixin,)
    text_enabled = True
    render_template = 'cascade/link/text-link.html'
    ring_plugin = 'TextLinkPlugin'
    fields = ['link_content'] + list(LinkPluginBase.fields)
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
