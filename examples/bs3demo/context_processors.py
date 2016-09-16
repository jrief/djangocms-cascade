# -*- coding: utf-8 -*-
from django.conf import settings


def cascade(request):
    """
    Adds additional context variables to the default context.
    """
    context = {
        'DJANGO_CLIENT_FRAMEWORK': settings.CMSPLUGIN_CASCADE['bootstrap3'].get('template_basedir'),
    }
    return context
