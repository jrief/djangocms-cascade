# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import GlossaryField
from cmsplugin_cascade.plugin_base import CascadePluginBase


class Badge(CascadePluginBase):
    name = _("Badge")
    require_parent = False
    allow_children = False
    render_template = 'bs3demo/badge.html'

    content = GlossaryField(widgets.TextInput(), label=_("Content"))

plugin_pool.register_plugin(Badge)
