# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.text import mark_safe
from django.utils.translation import ugettext_lazy as _

from cmsplugin_cascade.settings import CMSPLUGIN_CASCADE, orig_config

CASCADE_PLUGINS = ['map']

CMSPLUGIN_CASCADE.setdefault('leaflet', orig_config.get('leaflet', {}))
CMSPLUGIN_CASCADE['leaflet'].setdefault('tilesURL', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
CMSPLUGIN_CASCADE['leaflet'].setdefault('default_position', {'lat': 30.0, 'lng': -40.0, 'zoom': 3});
CMSPLUGIN_CASCADE['leaflet'].setdefault('id', 'mapbox.streets'),
CMSPLUGIN_CASCADE['leaflet'].setdefault('maxZoom', 18),
CMSPLUGIN_CASCADE['leaflet'].setdefault('detectRetina', True)
CMSPLUGIN_CASCADE['leaflet'].setdefault('attribution', mark_safe('Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>')),
