import io
import mimetypes
import os
from django.conf import settings
from django.conf.urls import url
from django.core.exceptions import ViewDoesNotExist
from django.http.response import HttpResponse
from django.views.generic import TemplateView
from django.utils.cache import patch_cache_control
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class SphinxDocsView(TemplateView):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug', '')
        _, extension = os.path.splitext(slug)
        if extension in ['.png', '.jpg', '.jpeg', '.gif']:
            filename = os.path.join(settings.SPHINX_DOCS_ROOT, slug)
            content_type, _ = mimetypes.guess_type(filename)
            with io.open(filename, 'rb') as fd:
                response = HttpResponse(content=fd.read(), content_type=content_type)
                patch_cache_control(response, cache_control='max-age=86400')
                return response
        return super().get(request, page=slug, *args, **kwargs)

    def get_template_names(self):
        return [self.request.current_page.get_template()]

    def get_context_data(self, page='index.html', **kwargs):
        context = super().get_context_data(**kwargs)
        filename = os.path.join(settings.SPHINX_DOCS_ROOT, page, 'index.html')
        if not os.path.exists(filename):
            raise ViewDoesNotExist("{} does not exist".format(page))
        with io.open(filename, encoding='utf-8') as fd:
            context.update(page_content=mark_safe(fd.read()))
        return context


@apphook_pool.register
class SphinxDocsApp(CMSApp):
    name = _("Sphinx Documentation")

    def get_urls(self, page=None, language=None, **kwargs):
        return [
            url(r'^(?P<slug>\S+)/$', SphinxDocsView.as_view(), name='sphinx-documentation'),
        ]
