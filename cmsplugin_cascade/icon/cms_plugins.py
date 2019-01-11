# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.conf.urls import url
from django.forms import widgets
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.models import CascadePage
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, LinkForm
from cmsplugin_cascade.widgets import CascadingSizeWidget, SetBorderWidget, ColorPickerWidget
from .mixins import IconPluginMixin, IconModelMixin


class FramedIconPlugin(IconPluginMixin, CascadePluginBase):
    name = _("Icon with frame")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/icon.html'
    model_mixins = (IconModelMixin,)
    ring_plugin = 'FramedIconPlugin'
    SIZE_CHOICES = [('{}em'.format(c), "{} em".format(c)) for c in range(1, 13)]
    RADIUS_CHOICES = [(None, _("Square"))] + \
        [('{}px'.format(r), "{} px".format(r)) for r in (1, 2, 3, 5, 7, 10, 15, 20)] + \
        [('50%', _("Circle"))]

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    font_size = GlossaryField(
        CascadingSizeWidget(allowed_units=['px', 'em']),
        label=_("Icon size"),
        initial='1em',
    )

    color = GlossaryField(
        ColorPickerWidget(),
        label=_("Icon color"),
    )

    background_color = GlossaryField(
        ColorPickerWidget(),
        label=_("Background color"),
    )

    text_align = GlossaryField(
        widgets.RadioSelect(choices=[
            ('', _("Do not align")),
            ('text-left', _("Left")),
            ('text-center', _("Center")),
            ('text-right', _("Right"))
        ]),
        label=_("Text alignment"),
        initial='',
        help_text=_("Align the icon inside the parent column.")
    )

    border = GlossaryField(
        SetBorderWidget(),
        label=_("Set border"),
    )

    border_radius = GlossaryField(
        widgets.Select(choices=RADIUS_CHOICES),
        label=_("Border radius"),
    )

    glossary_field_order = ['symbol', 'text_align', 'font_size', 'color', 'background_color', 'border', 'border_radius']

    class Media:
        js = ['cascade/js/admin/framediconplugin.js']

    @classmethod
    def get_tag_type(self, instance):
        if instance.glossary.get('text_align') or instance.glossary.get('font_size'):
            return 'div'

    @classmethod
    def get_css_classes(cls, instance):
        css_classes = cls.super(FramedIconPlugin, cls).get_css_classes(instance)
        text_align = instance.glossary.get('text_align')
        if text_align:
            css_classes.append(text_align)
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(FramedIconPlugin, cls).get_inline_styles(instance)
        inline_styles['font-size'] = instance.glossary.get('font_size', '1em')
        return inline_styles

plugin_pool.register_plugin(FramedIconPlugin)


class TextIconModelMixin(object):
    @cached_property
    def icon_font_class(self):
        icon_font = self.plugin_class.get_icon_font(self)
        symbol = self.glossary.get('symbol')
        if icon_font and symbol:
            return mark_safe('class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol))
        return ''


class TextIconPlugin(IconPluginMixin, LinkPluginBase):
    name = _("Icon in text")
    text_enabled = True
    render_template = 'cascade/plugins/texticon.html'
    ring_plugin = 'IconPlugin'
    parent_classes = ('TextPlugin',)
    model_mixins = (TextIconModelMixin, LinkElementMixin,)
    allow_children = False
    require_parent = False

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    color = GlossaryField(
        ColorPickerWidget(),
        label=_("Icon color"),
    )

    glossary_field_order = ['symbol', 'color']

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

    def get_form(self, request, obj=None, **kwargs):
        LINK_TYPE_CHOICES = [('none', _("No Link"))]
        LINK_TYPE_CHOICES.extend(getattr(LinkForm, 'LINK_TYPE_CHOICES'))
        Form = type(str('TextIconForm'), (getattr(LinkForm, 'get_form_class')(),),
                    {'LINK_TYPE_CHOICES': LINK_TYPE_CHOICES})
        kwargs.update(form=Form)
        return super(TextIconPlugin, self).get_form(request, obj, **kwargs)

    def get_plugin_urls(self):
        urls = [
            url(r'^wysiwig-config\.js$', self.render_wysiwig_config,
                name='cascade_texticon_wysiwig_config'),
        ]
        return urls

    def render_wysiwig_config(self, request):
        """Find the icon font associated to the CMS page, from which this subrequest is originating."""
        context = {}
        # Since this request is originating from CKEditor, we have no other choice rather than using
        # the referer, to determine the current CMS page.
        referer = urlparse(request.META['HTTP_REFERER'])
        matches = re.match(r'.+/edit-plugin/(\d+)/$', referer.path)
        if matches:
            cms_plugin = CMSPlugin.objects.get(id=matches.group(1))
            try:
                context['icon_font'] = cms_plugin.page.cascadepage.icon_font
            except CascadePage.DoesNotExist:
                pass
        javascript = render_to_string('cascade/admin/ckeditor.wysiwyg.txt', context)
        return HttpResponse(javascript, content_type='application/javascript')

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(TextIconPlugin, cls).get_inline_styles(instance)
        color = instance.glossary.get('color')
        if isinstance(color, list) and len(color) == 2 and not color[0]:
            inline_styles['color'] = color[1]
        return inline_styles

plugin_pool.register_plugin(TextIconPlugin)
