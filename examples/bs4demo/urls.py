# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from cmsplugin_cascade.theme.urls import extra_cascade_theme_patterns

class CascadeDemoView(TemplateView):
    template_name = 'bs4demo/strides.html'


admin.autodiscover()

urlpatterns = [
    path('admin/select2/', include('django_select2.urls')),
    path('admin/', admin.site.urls),
    path('cascade/', CascadeDemoView.as_view()),
    path('', include(extra_cascade_theme_patterns)),
    path('', include('cms.urls')),
]
urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
