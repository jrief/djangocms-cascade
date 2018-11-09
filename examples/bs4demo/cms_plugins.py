# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase


class Badge(CascadePluginBase):
    """
    This is a simple example of a plugin suitable for the djangocms-cascade system.
    It contains one single field: `content` rendered via the template `bs4demo/badge.html`.
    """
    name = _("Badge")
    require_parent = False
    allow_children = False
    render_template = 'bs4demo/badge.html'

    content = GlossaryField(
        widgets.TextInput(),
        label=_("Content"),
    )

plugin_pool.register_plugin(Badge)
