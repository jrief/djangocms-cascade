# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.http.response import JsonResponse, HttpResponseNotFound
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from cmsplugin_cascade.models import IconFont
from cmsplugin_cascade.plugin_base import CascadePluginMixinBase


class IconModelMixin(object):
    @property
    def icon_font_attrs(self):
        icon_font = self.plugin_class.get_icon_font(self)
        symbol = self.glossary.get('symbol')
        attrs = []
        if icon_font and symbol:
            attrs.append(mark_safe('class="{}{}"'.format(icon_font.config_data.get('css_prefix_text', 'icon-'), symbol)))
        styles = {
            'display': 'inline-block',
            'color': self.glossary.get('color', '#000000'),
        }
        disabled, background_color = self.glossary.get('background_color', (True, '#000000'))
        if not disabled:
            styles['background-color'] = background_color
        border = self.glossary.get('border')
        if isinstance(border, list) and border[0] and border[1] != 'none':
            styles.update(border='{0} {1} {2}'.format(*border))
            radius = self.glossary.get('border_radius')
            if radius:
                styles['border-radius'] = radius
        attrs.append(format_html('style="{}"',
                                 format_html_join('', '{0}:{1};',
                                                  [(k , v) for k, v in styles.items()])))
        return mark_safe(' '.join(attrs))


class IconPluginMixin(CascadePluginMixinBase):
    change_form_template = 'cascade/admin/fonticon_plugin_change_form.html'
    ring_plugin = 'IconPlugin'

    class Media:
        css = {'all': ['cascade/css/admin/iconplugin.css']}
        js = ['cascade/js/admin/iconplugin.js']

    @classmethod
    def get_identifier(cls, instance):
        identifier = super(IconPluginMixin, cls).get_identifier(instance)
        icon_font = cls.get_icon_font(instance)
        if icon_font:
            symbol = mark_safe('{}: <i class="{}{}"></i>'.format(
                icon_font.identifier,
                icon_font.config_data.get('css_prefix_text', 'icon-'),
                instance.glossary.get('symbol')))
            return format_html('{0}{1}', identifier, symbol)
        return identifier

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super(IconPluginMixin, self).changeform_view(
             request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, **kwargs):
        icon_font_field = [gf for gf in self.glossary_fields if gf.name == 'icon_font'][0]
        icon_font_field.widget.choices = IconFont.objects.values_list('id', 'identifier')
        form = super(IconPluginMixin, self).get_form(request, obj=obj, **kwargs)
        return form

    def get_plugin_urls(self):
        urlpatterns = [
            url(r'^fetch_fonticons/(?P<iconfont_id>[0-9]+)$', self.fetch_fonticons),
            url(r'^fetch_fonticons/$', self.fetch_fonticons, name='fetch_fonticons'),
        ]
        urlpatterns.extend(super(IconPluginMixin, self).get_plugin_urls())
        return urlpatterns

    def fetch_fonticons(self, request, iconfont_id=None):
        try:
            icon_font = IconFont.objects.get(id=iconfont_id)
        except IconFont.DoesNotExist:
            return HttpResponseNotFound("IconFont with id={} does not exist".format(iconfont_id))
        else:
            data = dict(icon_font.config_data)
            data.pop('glyphs', None)
            data['families'] = icon_font.get_icon_families()
            return JsonResponse(data)

    @classmethod
    def get_icon_font(self, instance):
        if not hasattr(instance, '_cached_icon_font'):
            try:
                instance._cached_icon_font = IconFont.objects.get(id=instance.glossary.get('icon_font') or 0)
            except IconFont.DoesNotExist:
                instance._cached_icon_font = None
        return instance._cached_icon_font

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        icon_font = self.get_icon_font(instance)
        if icon_font:
            context['stylesheet_url'] = icon_font.get_stylesheet_url()
        return context
