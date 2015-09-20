# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cmsplugin_cascade.plugin_base import CascadePluginBase


class FoundationPluginBase(CascadePluginBase):
    module = 'Foundation'
    require_parent = True
    allow_children = True
    render_template = 'cascade/generic/wrapper.html'
