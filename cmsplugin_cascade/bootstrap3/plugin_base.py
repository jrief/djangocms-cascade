# -*- coding: utf-8 -*-
from django.utils.six import with_metaclass
from cmsplugin_cascade.plugin_base import CascadePluginBaseMetaclass, CascadePluginBase
from cmsplugin_cascade.models import CascadeElement
from . import settings


class BootstrapPluginBaseMetaclass(CascadePluginBaseMetaclass):
    plugins_with_extrafields = settings.CASCADE_PLUGINS_WITH_EXTRAFIELDS


class BootstrapPluginBase(with_metaclass(BootstrapPluginBaseMetaclass, CascadePluginBase)):
    module = 'Bootstrap'
    model = CascadeElement
    require_parent = True
    allow_children = True
