# -*- coding: utf-8 -*-
from .models_base import LinkElementBase


class LinkElement(LinkElementBase):
    """
    A model class to adding an internal or external Link plus arbitrary context data.
    """
    class Meta:
        app_label = 'cmsplugin_cascade'
