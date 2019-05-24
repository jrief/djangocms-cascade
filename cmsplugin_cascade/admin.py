from django.conf.urls import url
from django.contrib import admin
from django.forms import widgets
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.translation import get_language_from_request
from cms.models.pagemodel import Page
from cms.extensions import PageExtensionAdmin
from cmsplugin_cascade.models import CascadePage, IconFont
from cmsplugin_cascade.link.forms import format_page_link


@admin.register(CascadePage)
class CascadePageAdmin(PageExtensionAdmin):
    add_form_template = change_form_template = 'cascade/admin/fonticon_change_form.html'
    fields = ['icon_font', 'menu_symbol']

    @property
    def media(self):
        media = super(CascadePageAdmin, self).media
        media.add_css({'all': ['cascade/css/admin/cascadepage.css']})
        media.add_js(['cascade/js/admin/cascadepage.js'])
        return media

    def get_form(self, request, obj=None, **kwargs):
        options = dict(kwargs, widgets={'menu_symbol': widgets.HiddenInput})
        ModelForm = super(CascadePageAdmin, self).get_form(request, obj, **options)
        return ModelForm

    def get_urls(self):
        urls = [
            url(r'^get_page_sections/$', lambda: None, name='get_page_sections'),  # just to reverse
            url(r'^get_page_sections/(?P<page_pk>\d+)$',
                self.admin_site.admin_view(self.get_page_sections)),
            url(r'^published_pages/$', self.get_published_pagelist, name='get_published_pagelist'),
            url(r'^fetch_fonticons/(?P<iconfont_id>[0-9]+)$', self.fetch_fonticons),
            url(r'^fetch_fonticons/$', self.fetch_fonticons, name='fetch_fonticons'),
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
        This view is used by the SearchLinkField as the user types to feed the autocomplete drop-down.
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

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = dict(extra_context or {}, icon_fonts=IconFont.objects.all())
        return super(CascadePageAdmin, self).changeform_view(
             request, object_id=object_id, form_url=form_url, extra_context=extra_context)
