# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.text import mark_safe

from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE, orig_config

CASCADE_PLUGINS = ['map']

CMSPLUGIN_CASCADE.setdefault('leaflet', orig_config.get('leaflet', {}))
CMSPLUGIN_CASCADE['leaflet'].setdefault('tilesURL', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
CMSPLUGIN_CASCADE['leaflet'].setdefault('id', 'mapbox.streets'),
CMSPLUGIN_CASCADE['leaflet'].setdefault('maxZoom', 18),
CMSPLUGIN_CASCADE['leaflet'].setdefault('detectRetina', True)
CMSPLUGIN_CASCADE['leaflet'].setdefault('attribution', mark_safe('Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>')),
