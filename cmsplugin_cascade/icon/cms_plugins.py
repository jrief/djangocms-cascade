# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.forms import widgets
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.widgets import CascadingSizeWidget, SetBorderWidget, ColorPickerWidget
from .mixins import IconPluginMixin, IconModelMixin


class FramedIconPlugin(IconPluginMixin, CascadePluginBase):
    name = _("Icon")
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

    icon_font = GlossaryField(
        widgets.Select(),
        label=_("Font"),
    )

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
        widgets.TextInput(attrs={'style': 'width: 5em;', 'type': 'color'}),
        label=_("Icon color"),
    )

    background_color = GlossaryField(
        ColorPickerWidget(),
        label=_("Background color"),
    )

    text_align = GlossaryField(
        widgets.RadioSelect(
            choices=(('', _("Do not align")), ('text-left', _("Left")),
                     ('text-center', _("Center")), ('text-right', _("Right")))),
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

    glossary_field_order = ('icon_font', 'symbol', 'text_align', 'font_size',
                            'color', 'background_color', 'border', 'border_radius')

    class Media:
        js = ['cascade/js/admin/framediconplugin.js']

    @classmethod
    def get_tag_type(self, instance):
        if instance.glossary.get('text_align'):
            return 'div'

    @classmethod
    def get_css_classes(cls, instance):
        css_classes = super(FramedIconPlugin, cls).get_css_classes(instance)
        text_align = instance.glossary.get('text_align')
        if text_align:
            css_classes.append(text_align)
        return css_classes

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = super(FramedIconPlugin, cls).get_inline_styles(instance)
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


class TextIconPlugin(IconPluginMixin, CascadePluginBase):
    name = _("Icon")
    text_enabled = True
    render_template = 'cascade/plugins/texticon.html'
    ring_plugin = 'IconPlugin'
    parent_classes = ('TextPlugin',)
    model_mixins = (TextIconModelMixin,)
    allow_children = False
    require_parent = False

    icon_font = GlossaryField(
        widgets.Select(),
        label=_("Font"),
    )

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    glossary_field_order = ('icon_font', 'symbol')

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

    def get_plugin_urls(self):
        urls = [
            url(r'^wysiwig-config.js$', self.render_wysiwig_config,
                name='cascade_texticon_wysiwig_config'),
        ]
        return urls

    def render_wysiwig_config(self, request):
        context = {
            'icon_fonts': IconFont.objects.all()
        }
        javascript = render_to_string('cascade/admin/ckeditor.wysiwyg.txt', context)
        return HttpResponse(javascript, content_type='application/javascript')

plugin_pool.register_plugin(TextIconPlugin)
