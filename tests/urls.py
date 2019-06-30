from django import VERSION as DJANGO_VERSION
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

if DJANGO_VERSION < (2, 0):
    from django.conf.urls import url, include

    urlpatterns = i18n_patterns(
        url(r'^admin/', admin.site.urls),
        url(r'^', include('cms.urls')),
    )

if DJANGO_VERSION >= (2, 0):
    from django.urls import path, include

    urlpatterns = i18n_patterns(
        path('admin/', admin.site.urls),
        path('', include('cms.urls')),
    )
