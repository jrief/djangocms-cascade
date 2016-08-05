# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, io, json, shutil
from collections import OrderedDict
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.http import JsonResponse
from django.utils.html import format_html, format_html_join
from django.utils.six.moves.urllib.parse import urljoin
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade.models import CascadePage, IconFont
from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE
import tempfile
try:
    import czipfile as zipfile
except ImportError:
    import zipfile


@admin.register(CascadePage)
class CascadePageAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict to hide the model from admin index.
        """
        return {}

    def get_urls(self):
        urls = [
            url(r'^get_page_sections/$', lambda: None, name='get_page_sections'),  # just to reverse
            url(r'^get_page_sections/(?P<page_pk>\d+)$',
                self.admin_site.admin_view(self.get_page_sections)),
        ]
        urls.extend(super(CascadePageAdmin, self).get_urls())
        return urls

    def get_page_sections(self, request, page_pk=None):
        choices = []
        try:
            for key, val in self.model.objects.get(extended_object_id=page_pk).glossary['element_ids'].items():
                choices.append((key, val))
        except (self.model.DoesNotExist, KeyError):
            pass
        return JsonResponse({'element_ids': choices})


class UploadIconsForms(ModelForm):
    class Meta:
        fields = ('identifier', 'zip_file')

    @property
    def media(self):
        media = super(UploadIconsForms, self).media
        if self.instance:
            icon_font_url = os.path.relpath(CMSPLUGIN_CASCADE['icon_font_root'], settings.MEDIA_ROOT)
            parts = (icon_font_url, self.instance.font_folder, 'css', 'fontello.css')
            css_url = urljoin(settings.MEDIA_URL, '/'.join(parts))
            media.add_css({'all': ('cascade/css/admin/iconfont.css', css_url,)})
        return media

    def unzip_archive(self, zip_ref):
        common_prefix = os.path.commonprefix(zip_ref.namelist())
        if not common_prefix:
            raise ValidationError(_("The uploaded zip archive is not packed correctly"))
        try:
            temp_folder = tempfile.mkdtemp(prefix='', dir=CMSPLUGIN_CASCADE['icon_font_root'])
            for member in zip_ref.infolist():
                zip_ref.extract(member, temp_folder)
            font_folder = os.path.join(temp_folder, common_prefix)

            # this is specific to fontello
            fh = io.open(os.path.join(font_folder, 'config.json'), 'r')
            config_data = json.load(fh)
        except Exception as e:
            shutil.rmtree(temp_folder, ignore_errors=True)
            raise ValidationError(_("Can not unzip uploaded archive. Reason: {}").__format__(e))
        return os.path.relpath(font_folder, CMSPLUGIN_CASCADE['icon_font_root']), config_data

    def clean(self):
        cleaned_data = super(UploadIconsForms, self).clean()
        if 'zip_file' in self.changed_data:
            try:
                zip_ref = zipfile.ZipFile(cleaned_data['zip_file'].file.file, 'r')
                cleaned_data.update(zip(['font_folder', 'config_data'], self.unzip_archive(zip_ref)))
            finally:
                zip_ref.close()
        return cleaned_data


@admin.register(IconFont)
class IconFontAdmin(admin.ModelAdmin):
    form = UploadIconsForms
    readonly_fields = ('preview_icons',)

    def save_model(self, request, obj, form, change):
        if 'font_folder' in form.cleaned_data and 'config_data' in form.cleaned_data:
            obj.font_folder = form.cleaned_data['font_folder']
            obj.config_data = form.cleaned_data['config_data']
        super(IconFontAdmin, self).save_model(request, obj, form, change)

    def preview_icons(self, obj):
        if obj is None:
            return
        families = OrderedDict()
        for glyph in obj.config_data['glyphs']:
            src = glyph.pop('src', 'default')
            families.setdefault(src, [])
            families[src].append(glyph)
        format_string = '<li title="{css_prefix_text}{{0}}"><i class="{css_prefix_text}{{0}}"></i></li>'.format(**obj.config_data)
        return format_html('<div class="preview-iconfont">{}</div>',
            format_html_join('\n', '<h2>{}</h2><ul>{}</ul>',
                 ((src.title(), format_html_join('', format_string, ((g['css'],) for g in glyphs)))
                 for src, glyphs in families.items())))
    preview_icons.short_description = _("Preview Icons")
    preview_icons.allow_tags = True
