# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings
from django.contrib.admin.utils import unquote
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from cmsplugin_cascade.models import CascadePage, IconFont
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase


class IconPluginMixin(CascadePluginMixinBase):
    change_form_template = 'cascade/admin/fonticon_plugin_change_form.html'
    ring_plugin = 'IconPluginMixin'
    require_icon_font = True  # if False, the icon_font is optional

    class Media:
        css = {'all': ['cascade/css/admin/iconplugin.css']}
        js = ['cascade/js/admin/iconpluginmixin.js']

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(IconPluginMixin, cls).get_identifier(instance)
        icon_font = cls.get_icon_font(instance)
        if icon_font:
            symbol = mark_safe('<i class="{}{}"></i>'.format(
                icon_font.config_data.get('css_prefix_text', 'icon-'),
                instance.glossary.get('symbol')))
            return format_html('{0}{1}', identifier, symbol)
        return identifier

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:  # to find the the CMS page in which this plugin is added, from there find the selected icon_font
            if object_id:
                icon_font = self.get_object(request, unquote(object_id)).cmsplugin_ptr.page.cascadepage.icon_font
            else:
                icon_font = self._cms_initial_attributes['placeholder'].page.cascadepage.icon_font
        except (AttributeError, CascadePage.DoesNotExist):
            icon_font = None
        if not icon_font:
            icon_font = IconFont.objects.filter(is_default=True).first()
        extra_context = dict(extra_context or {}, icon_font=icon_font, require_icon_font=self.require_icon_font)
        return super(IconPluginMixin, self).changeform_view(
             request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    @classmethod
    def get_icon_font(self, instance):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                icon_font = instance.cmsplugin_ptr.page.cascadepage.icon_font
        except (CascadePage.DoesNotExist, AttributeError):
            icon_font = None
        if not icon_font:
            icon_font = IconFont.objects.filter(is_default=True).first()
        return icon_font

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        icon_font = self.get_icon_font(instance)
        if icon_font:
            context['stylesheet_url'] = icon_font.get_stylesheet_url()
        return context
