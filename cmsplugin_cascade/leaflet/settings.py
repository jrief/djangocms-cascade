from django.utils.safestring import mark_safe

CASCADE_PLUGINS = ['map']

def set_defaults(config):
    config.setdefault('leaflet', {})
    config['leaflet'].setdefault('tilesURL', 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
    config['leaflet'].setdefault('default_position', {'lat': 30.0, 'lng': -40.0, 'zoom': 3})
    config['leaflet'].setdefault('id', 'mapbox/streets-v11'),
    config['leaflet'].setdefault('maxZoom', 18),
    config['leaflet'].setdefault('tileSize', 512)
    config['leaflet'].setdefault('zoomOffset', -1)
    config['leaflet'].setdefault('detectRetina', True)
    config['leaflet'].setdefault('attribution', mark_safe('Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>')),
