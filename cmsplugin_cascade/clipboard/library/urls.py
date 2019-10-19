from cmsplugin_cascade.clipboard.library import views
from django.conf.urls import url
from django.conf import settings


if getattr(settings, 'CASCADE_CLIPS_LIBRARY', None):
    extra_cascade_patterns = [url(r'cascade_copytoclipboard/$',
                                  views.CascadeCopyToClipboard.as_view(),
                                  name='cascade_copytoclipboard'),
                              url(r'cascade_clips/(\d+)/$',
                                  views.CascadeLibClips,
                                  name='cascade_clips'),
                              url(r'cascade_clips_folder/(\d+)/$',
                                  views.CascadeLibClipsFolder,
                                  name='cascade_clips_folder'),
                              ]
else:
    extra_cascade_patterns = []
