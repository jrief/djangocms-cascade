from urllib.parse import urlparse
import requests

from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.forms import Media, widgets
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.urls import re_path, reverse
from django.utils.translation import get_language_from_request

from cms.models.pagemodel import Page
from cms.extensions import PageExtensionAdmin
from cms.utils.page import get_page_from_path
from cmsplugin_cascade.models import CascadePage, IconFont
from cmsplugin_cascade.link.forms import format_page_link


@admin.register(CascadePage)
class CascadePageAdmin(PageExtensionAdmin):
    add_form_template = change_form_template = 'cascade/admin/change_form.html'
    fields = ['icon_font', 'menu_symbol']

    @property
    def media(self):
        media = super().media
        media += Media(css={'all': ['cascade/css/admin/cascadepage.css']},
                       js=['admin/js/jquery.init.js', 'cascade/js/admin/cascadepage.js'])
        return media

    def get_form(self, request, obj=None, **kwargs):
        options = dict(kwargs, widgets={'menu_symbol': widgets.HiddenInput})
        ModelForm = super().get_form(request, obj, **options)
        return ModelForm

    def get_urls(self):
        urls = [
            re_path(r'^get_page_sections/$', lambda _: JsonResponse({'element_ids': []}),
                name='get_page_sections'),  # just to reverse
            re_path(r'^get_page_sections/(?P<page_pk>\d+)$',
                self.admin_site.admin_view(self.get_page_sections)),
            re_path(r'^published_pages/$', self.get_published_pagelist, name='get_published_pagelist'),
            re_path(r'^fetch_fonticons/(?P<iconfont_id>[0-9]+)$', self.fetch_fonticons),
            re_path(r'^fetch_fonticons/$', self.fetch_fonticons, name='fetch_fonticons'),
            re_path(r'^validate_exturl/$', self.validate_exturl, name='validate_exturl'),
        ]
        urls.extend(super().get_urls())
        return urls

    def get_page_sections(self, request, page_pk=None):
        choices = []
        try:
            extended_glossary = self.model.objects.get(extended_object_id=page_pk).glossary
            for key, val in extended_glossary['element_ids'].items():
                choices.append((key, val))
        except (self.model.DoesNotExist, KeyError):
            pass
        return JsonResponse({'element_ids': choices})

    def get_published_pagelist(self, request, *args, **kwargs):
        """
        This view is used by the SearchLinkField as the user types to feed the autocomplete drop-down.
        """
        if not request.is_ajax():
            return HttpResponseForbidden()
        data = {'results': []}
        language = get_language_from_request(request)
        query_term = request.GET.get('term')
        if not query_term:
            return JsonResponse(data)

        # first, try to resolve by URL if it points to a local resource
        parse_result = urlparse(query_term)
        if parse_result.netloc.split(':')[0] == request.META['HTTP_HOST'].split(':')[0]:
            site = get_current_site(request)
            path = parse_result.path.lstrip(reverse('pages-root')).rstrip('/')
            page = get_page_from_path(site, path)
            if page:
                data['results'].append(self.get_result_set(language, page))
                return JsonResponse(data)

        # otherwise resolve by search term
        matching_published_pages = Page.objects.published().public().filter(
            Q(title_set__title__icontains=query_term, title_set__language=language)
            | Q(title_set__path__icontains=query_term, title_set__language=language)
            | Q(title_set__menu_title__icontains=query_term, title_set__language=language)
            | Q(title_set__page_title__icontains=query_term, title_set__language=language)
        ).distinct().order_by('title_set__title').iterator()

        for page in matching_published_pages:
            data['results'].append(self.get_result_set(language, page))
            if len(data['results']) > 15:
                break
        return JsonResponse(data)

    def get_result_set(self, language, page):
        title = page.get_title(language=language)
        path = page.get_absolute_url(language=language)
        return {
            'id': page.pk,
            'text': format_page_link(title, path),
        }

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

    def validate_exturl(self, request):
        """
        Perform a GET request onto the given external URL and return its status.
        """
        exturl = request.GET.get('exturl')
        request_headers = {'User-Agent': 'Django-CMS-Cascade'}
        try:
            response = requests.get(exturl, allow_redirects=True, headers=request_headers)
        except Exception:
            return JsonResponse({'status_code': 500})
        else:
            return JsonResponse({'status_code': response.status_code})

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super().changeform_view(
             request, object_id=object_id, form_url=form_url, extra_context=extra_context)
