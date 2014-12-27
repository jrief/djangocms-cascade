# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from cmsplugin_cascade.plugin_base import CascadePluginBase


class BootstrapPluginBase(CascadePluginBase):
    module = 'Bootstrap'
    require_parent = True
    allow_children = True
