from django.conf.urls import include, url
from django.conf import settings
from cmsplugin_cascade.theme.views import myview, CascadePreferenceFormView

if getattr(settings, 'CASCADE_THEME', None):
    extra_cascade_theme_patterns = [
    url(r'^theme/',CascadePreferenceFormView.as_view()),
    ]
else:
    extra_cascade_theme_patterns = []
