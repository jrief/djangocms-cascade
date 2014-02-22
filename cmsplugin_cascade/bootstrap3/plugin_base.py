# -*- coding: utf-8 -*-
from cmsplugin_cascade.plugin_base import CascadePluginBase
from cmsplugin_cascade.cms_plugins import framework


class BootstrapPluginBase(CascadePluginBase):
    module = framework == 'angular_bootstrap3' and 'Angular Bootstrap' or 'Bootstrap'
    require_parent = True
    allow_children = True
