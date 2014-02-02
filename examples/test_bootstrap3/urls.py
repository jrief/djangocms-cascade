# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
