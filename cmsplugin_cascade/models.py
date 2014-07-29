# -*- coding: utf-8 -*-
from .models_base import CascadeModelBase


class CascadeElement(CascadeModelBase):
    class Meta:
        app_label = 'cmsplugin_cascade'
