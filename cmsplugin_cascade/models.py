# -*- coding: utf-8 -*-
from django.utils.importlib import import_module
from .models_base import CascadeModelBase


class CascadeElement(CascadeModelBase):
    pass

import_module('.link.models', 'cmsplugin_cascade')  # HACK: make this configurable
import_module('.image.models', 'cmsplugin_cascade')  # HACK: make this configurable
