# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple


PluginExtraFieldsConfig = namedtuple('PluginExtraFields', ('allow_id_tag', 'css_classes', 'inline_styles'))

default_plugin_extra_fields = PluginExtraFieldsConfig(
    allow_id_tag=False,
    css_classes={'multiple': '', 'class_names': ''},
    inline_styles={},
)