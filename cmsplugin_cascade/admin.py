# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.translation import get_language_from_request
from cms.models.pagemodel import Page
from cms.extensions import PageExtensionAdmin
from cmsplugin_cascade.models import CascadePage
from cmsplugin_cascade.link.forms import format_page_link


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
            url(r'^published_pages/$', self.get_published_pagelist, name='get_published_pagelist'),
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

    def get_published_pagelist(self, request, *args, **kwargs):
        """
        This view is used by the SearchLinkField as the user type to feed the autocomplete drop-down.
        """
        if not request.is_ajax():
            return HttpResponseForbidden()

        query_term = request.GET.get('term','').strip('/')
        language = get_language_from_request(request)
        matching_published_pages = Page.objects.published().public().filter(
            Q(title_set__title__icontains=query_term, title_set__language=language)
            | Q(title_set__path__icontains=query_term, title_set__language=language)
            | Q(title_set__menu_title__icontains=query_term, title_set__language=language)
            | Q(title_set__page_title__icontains=query_term, title_set__language=language)
        ).distinct().order_by('title_set__title').iterator()

        data = {'results': []}
        for page in matching_published_pages:
            title = page.get_title(language=language)
            path = page.get_absolute_url(language=language)
            data['results'].append({
                'id': page.pk,
                'text': format_page_link(title, path),
            })
            if len(data['results']) > 15:
                break
        return JsonResponse(data)
