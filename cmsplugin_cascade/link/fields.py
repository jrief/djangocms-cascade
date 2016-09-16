# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
if 'django_select2' in settings.INSTALLED_APPS:
    from django_select2.fields import AutoModelSelect2Field
else:
    raise ImportError('django_select2 not configured')


class LinkSearchField(AutoModelSelect2Field):
    empty_value = []

    class Media:
        js = (settings.STATIC_ROOT + 'node_modules/jquery/dist/jquery.min.js',)

    def __init__(self, *args, **kwargs):
        try:
            self.search_fields = kwargs.pop('search_fields')
        except KeyError:
            pass
        super(LinkSearchField, self).__init__(*args, **kwargs)

    def security_check(self, request, *args, **kwargs):
        user = request.user
        if user and not user.is_anonymous() and user.is_staff:
            return True
        return False

    def prepare_value(self, value):
        if not value:
            return None
        return super(LinkSearchField, self).prepare_value(value)
