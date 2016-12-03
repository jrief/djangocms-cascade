# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class CascadeCustomBackend(ModelBackend):

    def __init__(self, *args, **kwargs):
        super(CascadeCustomBackend, self).__init__()

    def has_perm(self, user_obj, perm, obj=None):
        if perm.startswith('dummy_cmsplugin_cascade'):
            codename = perm.split('.', 1)[1]
            if not Permission.objects.filter(codename=codename).exists():
                perm_splitted = perm_splitted[1].split('_', 1)
                codename = '%s_bootstrapcontainerpluginmodel' % perm_splitted[0]
            perm = 'cmsplugin_cascade.%s' % codename
            return super(CascadeCustomBackend, self).has_perm(user_obj, perm, obj)