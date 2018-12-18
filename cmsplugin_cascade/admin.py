# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.http import JsonResponse

from cms.extensions import PageExtensionAdmin
from cmsplugin_cascade.models import CascadePage


@admin.register(CascadePage)
class CascadePageAdmin(PageExtensionAdmin):
    change_form_template = 'cascade/admin/cascadepage_change_form.html'

    def get_fields(self, request, obj=None):
        return ['icon_font']

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
