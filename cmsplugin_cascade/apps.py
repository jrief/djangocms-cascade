# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CascadeConfig(AppConfig):
    name = 'cmsplugin_cascade'
    verbose_name = _("django CMS Cascade")
