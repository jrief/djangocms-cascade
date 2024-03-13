from urllib.parse import urlparse
import requests

from django.contrib import admin
from django.forms import Media, widgets
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.urls import path, re_path
from django.utils.translation import get_language_from_request, get_language_from_path

from cms.models.contentmodels import PageContent
from cms.models.pagemodel import Page, PageUrl
from cms.extensions import PageContentExtensionAdmin, PageExtensionAdmin

from cmsplugin_cascade.models import CascadePage, CascadePageContent, IconFont
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
            re_path(r'^published_pages/$', self.get_published_pagelist, name='get_published_pagelist'),
            re_path(r'^fetch_fonticons/(?P<iconfont_id>[0-9]+)$', self.fetch_fonticons),
            re_path(r'^fetch_fonticons/$', self.fetch_fonticons, name='fetch_fonticons'),
            re_path(r'^validate_exturl/$', self.validate_exturl, name='validate_exturl'),
        ]
        urls.extend(super().get_urls())
        return urls

    def get_published_pagelist(self, request, *args, **kwargs):
        """
        This view is used by the SearchLinkField as the user types to feed the autocomplete drop-down.
        """
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return HttpResponseForbidden()
        data = {'results': []}
        language = get_language_from_request(request, check_path=True)
        search_term = request.GET.get('term').strip()
        if not search_term:
            return JsonResponse(data)

        # first, try to resolve by URL if it points to a local resource
        parse_result = urlparse(search_term)
        if parse_result.netloc.split(':')[0] == request.META['HTTP_HOST'].split(':')[0]:
            path = parse_result.path.strip('/')
            if get_language_from_path(parse_result.path):
                path = '/'.join(path.split('/')[1:])
            for page_url in PageUrl.objects.filter(path=path):
                page_content = page_url.page.get_content_obj(language)
                data['results'].append(self.get_result_set(page_content))
            return JsonResponse(data)

        # otherwise resolve by search term
        matching_page_contents = PageContent.objects.filter(
            Q(language=language) & (
                Q(title__icontains=search_term)
              | Q(page__urls__path__icontains=search_term)
              | Q(menu_title__icontains=search_term)
              | Q(page_title__icontains=search_term)
            )
        ).distinct().order_by('title').iterator()

        for page_content in matching_page_contents:
            data['results'].append(self.get_result_set(page_content))
            if len(data['results']) > 15:
                break
        return JsonResponse(data)

    def get_result_set(self, page_content):
        path = page_content.get_absolute_url()
        return {
            'id': page_content.page.pk,
            'text': format_page_link(page_content.title, path),
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
        if not exturl:
            return JsonResponse({})
        request_headers = {'User-Agent': 'Django-CMS-Cascade'}
        try:
            response = requests.get(exturl, allow_redirects=True, headers=request_headers, timeout=5.0)
        except Exception:
            return JsonResponse({'status_code': 500})
        else:
            return JsonResponse({'status_code': response.status_code})

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super().changeform_view(
             request, object_id=object_id, form_url=form_url, extra_context=extra_context)


@admin.register(CascadePageContent)
class CascadePageContentAdmin(PageContentExtensionAdmin):
    def get_urls(self):
        urls = [
            path('get_page_sections/', lambda _: JsonResponse({'element_ids': []}),
                name='get_page_sections'),  # just to reverse
            path('get_page_sections/<int:page_id>/',
                self.admin_site.admin_view(self.get_page_sections)),
        ]
        urls.extend(super().get_urls())
        return urls

    def get_page_sections(self, request, page_id=None):
        """
        This view is used to populate the select box nearby the CMS page's link field.
        """
        page = Page.objects.get(id=page_id)
        language = request.GET.get('language')
        choices = []
        try:
            page_content = page.get_content_obj(language, fallback=True)
            element_ids = page_content.cascadepagecontent.glossary['element_ids']
            for key, val in element_ids.items():
                if val:
                    choices.append((key, val))
        except (PageContent.DoesNotExist, self.model.DoesNotExist, KeyError):
            pass
        return JsonResponse({'element_ids': choices})
