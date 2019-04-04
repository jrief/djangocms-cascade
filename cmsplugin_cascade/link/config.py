# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _
from cmsplugin_cascade import app_settings


LinkPluginBase, LinkElementMixin, LinkForm = (import_string(cls)
    for cls in app_settings.CMSPLUGIN_CASCADE['link_plugin_classes'])


class VoluntaryLinkForm(LinkForm):
    """
    Plugins offering to link onto somethink, offer a field named 'Link' where the user can select the type of
    link. If linking is voluntary, that type has an additional option named "No Link" and subsequently linking
    becomes optional.
    """
    LINK_TYPE_CHOICES = [('none', _("No Link"))] + getattr(LinkForm, 'LINK_TYPE_CHOICES')
