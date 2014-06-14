# -*- coding: utf-8 -*-
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.models import CascadeElement


class BootstrapPluginBase(CascadePluginBase):
    module = 'Bootstrap'
    model = CascadeElement
    require_parent = True
    allow_children = True
