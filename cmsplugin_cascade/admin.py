# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin
from django.http import JsonResponse
from cmsplugin_cascade.models import CascadePage


@admin.register(CascadePage)
class CascadePageAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict to hide the model from admin index.
        """
        return {}

    def get_urls(self):
        return patterns('',
            url(r'^get_page_sections/$', lambda: None, name='get_page_sections'),  # just to reverse
            url(r'^get_page_sections/(?P<page_pk>\d+)$',
                self.admin_site.admin_view(self.get_page_sections)),
        ) + super(CascadePageAdmin, self).get_urls()

    def get_page_sections(self, request, page_pk=None):
        response = JsonResponse({'foo': 'bar'})
        return response
