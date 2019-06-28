import django
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

if django.get_version() < "2.0.0":    
    from django.conf.urls import url, include

    urlpatterns = i18n_patterns(
        url(r'^admin/', admin.site.urls),
        url(r'^', include('cms.urls')),
    )

if django.get_version() >= "2.0.0":    
    from django.urls import path, include

    urlpatterns = i18n_patterns(
        path('admin/', admin.site.urls),
        path('', include('cms.urls')),
    )
