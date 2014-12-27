# -*- coding: utf-8 -*-
from cmsplugin_cascade.cms_plugins import framework


def cascade(request):
    """
    Adds additional context variables to the default context.
    """
    context = {
        'framework': framework,
    }
    return context
