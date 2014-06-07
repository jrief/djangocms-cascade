# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns, include
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cms.urls')),
)
