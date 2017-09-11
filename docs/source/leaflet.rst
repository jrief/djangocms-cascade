.. _leaflet:

=====================================
Map Plugin using the Leaflet frontend
=====================================

If you want to add a interactive maps to a **Django-CMS** placeholder, the **Cascade Leaflet Map
Plugin** may be your best choice. It is not activated by default, because it requires a special
JavaScript library, an active Internet connection (in order to load the map tiles), and a license
key (this depends on the chosen tiles layer). By default the **Cascade Leaflet Map Plugin** uses
the `Open Street Map`_ tile layer, but this can be changed to Mapbox_, `Google Maps`_ or another
provider.

This plugin uses third party packages, based on the `Leaflet JavaScript`_ library for mobile-friendly
interactive maps.

.. _Open Street Map: http://www.openstreetmap.org/
.. _Mapbox: https://www.mapbox.com/
.. _Google Maps: https://developers.google.com/maps/
.. _Leaflet JavaScript: http://leafletjs.com/


Installation
============

The required JavaScript dependencies are not shipped with **djangocms-cascade**. They must be
installed separately from the `Node JS repository`_.

.. code-block:: shell

	npm install leaflet
	npm install leaflet-easybutton

.. note:: Leaflet Easybutton is only required for the administration backend.

.. _Node JS repository: https://www.npmjs.com/


Configuration
=============

The default Cascade settings must be active in order to use the **Leaflet Map Plugin**. Additionally
add to the project's settings:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = [
	    ...
	    'cmsplugin_cascade.leaflet',
	    ...
	]

By modifying the dictionary ``CMSPLUGIN_CASCADE['leaflet']`` you may override Leaflet specific
settings. Change ``CMSPLUGIN_CASCADE['leaflet']['tilesURL']`` to the `titles layer`_ of your choice.

All other attributes of that dictionary are passed as options to the Leaflet ``tileLayer``
constructor. For details, please refer to the Leaflet specific documentation.

.. _titles layer: http://leafletjs.com/reference-1.0.3.html#tilelayer


Usage
=====

Add a **Map Plugin** to any **django-CMS** placeholder. Here you may adjust the width and height of
the map.

The map can be repositioned at any time. Use the *Center* button on the top left corner to reset the
position to the coordinates and zoom level, it was saved the last time.


Adding a marker to the map
--------------------------

First click on *Add another Marker* and enter a title of your choice. Afterwards go to the map and
place the marker. After saving the map, this new marker will be persisted.

Additionally, one may choose a customized marker icon: Click on *Use customized marker icon* and
choose an image from your media files. It is recommended to use PNG images with a transparent layer
as marker icons.

Adjust the icon's size by setting the marker width. The height is computed in order to keep the same
aspect ratio.

.. note:: Customized marker icons are only displayed in the frontend. The backend always uses the
	default pin symbol.

By settings the marker's anchor, the icon can be positioned exactly.

Markers can be repositioned at any time and the new coordinates are saved together with the map.


Alternative Tiles
=================

By default, **djangocms-cascade** is shipped using tiles from the `Open Street Map`_ project.
This is mainly because these tiles can be used without requiring a license key. However, they load
slowly and their appearance might not be what your customers expect.


Mapbox
------

A good alternative are tiles from Mapbox_. Please refer to their terms and conditions for details.
There you can also apply for an access token, they offer free plans for low traffic sites.

Then add to the project's ``settings.py``:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'leaflet': {
	        'tilesURL': 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}',
	        'accessToken': YOUR-MAPBOX-ACCESS-TOKEN,
	        ...
	    }
	    ...
	}


Google Maps
-----------

The problem with Google is that its Terms of Use forbid any means of tile access other than through
the Google Maps API. Therefore in the frontend, Google Maps are rendered using a different template,
which is not based on the LeafletJS library. This means that you must edit your maps using Mapbox or
OpenStreetMap titles, whereas Google Maps is only rendered in the frontend.

To start with, apply for a `Google Maps API key`_ and add it to the project's ``settings.py``:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'leaflet': {
	        ...
	        'apiKey': YOUR-GOOGLE-MAPS-API-KEY,
	        ...
	    }
	    ...
	}

When editing a **Map** plugin, choose *Google Map* from the select field named *Render template*.

If want to render Google Maps exclusively in the frontend, change this in your project's
``settings.py``:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'plugins_with_extra_render_templates': {
	        'LeafletPlugin': [
	            ('cascade/plugins/googlemap.html', "Google Map"),
	        ],
	    }
	    ...
	}

.. _Google Maps API key: https://developers.google.com/maps/documentation/javascript/get-api-key


Default Starting Position
=========================

Depending of the region you normally create maps, you can specify the default starting position. If for instance
your main area of interest is Germany, than these coordinates are a good setting:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'leaflet': {
	        'default_position': {'lat': 50.0, 'lng': 12.0, 'zoom': 6},
	    }
	    ...
	}
