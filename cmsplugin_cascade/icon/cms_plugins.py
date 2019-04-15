# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.utils.functional import cached_property
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.link.config import LinkPluginBase, LinkElementMixin, VoluntaryLinkForm
from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.widgets import CascadingSizeWidget, SetBorderWidget, ColorPickerWidget
from .mixins import IconPluginMixin


def get_default_icon_font():
    try:
        return IconFont.objects.get(is_default=True).id
    except IconFont.DoesNotExist:
        return ''


class SimpleIconPlugin(IconPluginMixin, LinkPluginBase):
    name = _("Simple Icon")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/simpleicon.html'
    model_mixins = (LinkElementMixin,)
    fields = list(LinkPluginBase.fields)
    ring_plugin = 'IconPlugin'

    icon_font = GlossaryField(
        widgets.Select(),
        label=_("Font"),
        initial=get_default_icon_font,
    )

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    glossary_field_order = ['icon_font', 'symbol']

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(form=VoluntaryLinkForm.get_form_class())
        return super(SimpleIconPlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        context = super(SimpleIconPlugin, self).render(context, instance, placeholder)
        icon_font = self.get_icon_font(instance)
        symbol = instance.glossary.get('symbol')
        if icon_font and symbol:
            font_attr = 'class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol)
            context['icon_font_attrs'] = mark_safe(font_attr)
        return context

plugin_pool.register_plugin(SimpleIconPlugin)


class FramedIconPlugin(IconPluginMixin, LinkPluginBase):
    name = _("Icon with frame")
    parent_classes = None
    require_parent = False
    allow_children = False
    render_template = 'cascade/plugins/framedicon.html'
    model_mixins = (LinkElementMixin,)
    ring_plugin = 'FramedIconPlugin'
    fields = list(LinkPluginBase.fields)
    SIZE_CHOICES = [('{}em'.format(c), "{} em".format(c)) for c in range(1, 13)]
    RADIUS_CHOICES = [(None, _("Square"))] + \
        [('{}px'.format(r), "{} px".format(r)) for r in (1, 2, 3, 5, 7, 10, 15, 20)] + \
        [('50%', _("Circle"))]

    icon_font = GlossaryField(
        widgets.Select(),
        label=_("Font"),
        initial=get_default_icon_font,
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

    glossary_field_order = ['icon_font', 'symbol', 'text_align', 'font_size', 'color', 'background_color',
                            'border', 'border_radius']

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

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(form=VoluntaryLinkForm.get_form_class())
        return super(FramedIconPlugin, self).get_form(request, obj, **kwargs)

    def render(self, context, instance, placeholder):
        context = self.super(FramedIconPlugin, self).render(context, instance, placeholder)
        icon_font = self.get_icon_font(instance)
        symbol = instance.glossary.get('symbol')
        attrs = []
        if icon_font and symbol:
            attrs.append(mark_safe('class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol)))
        styles = {'display': 'inline-block'}
        disabled, color = instance.glossary.get('color', (True, '#000000'))
        if not disabled:
            styles['color'] = color
        disabled, background_color = instance.glossary.get('background_color', (True, '#000000'))
        if not disabled:
            styles['background-color'] = background_color
        border = instance.glossary.get('border')
        if isinstance(border, list) and border[0] and border[1] != 'none':
            styles.update(border='{0} {1} {2}'.format(*border))
            radius = instance.glossary.get('border_radius')
            if radius:
                styles['border-radius'] = radius
        attrs.append(format_html('style="{}"',
                                 format_html_join('', '{0}:{1};',
                                                  [(k, v) for k, v in styles.items()])))
        context['icon_font_attrs'] = mark_safe(' '.join(attrs))
        return context

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
    """
    This plugin is intended to be used inside the django-CMS-CKEditor.
    """
    name = _("Icon in text")
    text_enabled = True
    render_template = 'cascade/plugins/texticon.html'
    ring_plugin = 'IconPlugin'
    parent_classes = ['TextPlugin']
    model_mixins = (TextIconModelMixin, LinkElementMixin,)
    allow_children = False
    require_parent = False

    icon_font = GlossaryField(
        widgets.Select(),
        label=_("Font"),
        initial=get_default_icon_font,
    )

    symbol = GlossaryField(
        widgets.HiddenInput(),
        label=_("Select Symbol"),
    )

    color = GlossaryField(
        ColorPickerWidget(),
        label=_("Icon color"),
    )

    glossary_field_order = ['icon_font', 'symbol', 'color']

    class Media:
        js = ['cascade/js/admin/iconplugin.js']

    @classmethod
    def requires_parent_plugin(cls, slot, page):
        return False

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update(form=VoluntaryLinkForm.get_form_class())
        return super(TextIconPlugin, self).get_form(request, obj, **kwargs)

    @classmethod
    def get_inline_styles(cls, instance):
        inline_styles = cls.super(TextIconPlugin, cls).get_inline_styles(instance)
        color = instance.glossary.get('color')
        if isinstance(color, list) and len(color) == 2 and not color[0]:
            inline_styles['color'] = color[1]
        return inline_styles

plugin_pool.register_plugin(TextIconPlugin)
