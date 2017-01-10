# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.utils.text import force_text
from django.utils.translation import ugettext_lazy as _


class CascadeConfig(AppConfig):
    name = 'cmsplugin_cascade'
    verbose_name = _("django CMS Cascade")

    def ready(self):
        if 'cmsplugin_cascade.icon' in settings.INSTALLED_APPS:
            stylesSet = force_text(settings.CKEDITOR_SETTINGS.get('stylesSet'))
            if stylesSet != 'default:{}'.format(reverse('admin:cascade_texticon_wysiwig_config')):
                msg = "settings.CKEDITOR_SETTINGS['stylesSet'] should be `format_lazy('default:{}', reverse_lazy('admin:cascade_texticon_wysiwig_config'))`"
                raise ImproperlyConfigured(msg)
