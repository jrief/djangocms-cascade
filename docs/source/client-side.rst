.. _client-side:

========================
Handling the client side
========================

**DjangoCMS-Cascade** is shipped with a bunch of plugins with their own inheritance hierarchy.
Due to the flexibility of Cascade, this inheritance hierarchy can be configured during runtime.

On the client side, we would like to describe the same inheritance hierarchy using Javascript.
Therefore Cascade is equipped with a small, but very powerful library named ring.js_. It makes
Javascript behave almost like Python. If a Cascade plugin provides a Javascript counterpart,
then other Cascade plugins inheriting from the former one, map their inheritance hierarchy in
Javascript exactly as provided by the plugins written in Python.


Implementing the client
=======================

Say, we want to add some client side code to a Cascade plugin, then we first must import that
Javascript file through Django's media_ management. Since we also want to handle dependencies
of Javascript files, Cascade provides a utility function named ``resolve_dependencies``.

Our custom Cascade plugin then might look like:

.. code-block:: python

	from cmsplugin_cascade.plugin_base import CascadePluginBase
	from cmsplugin_cascade.utils import resolve_dependencies

	class MyCustomPlugin(CascadePluginBase):
	    name = "Custom Plugin"
	    ... other class attributes
	    ring_plugin = 'MyCustomPlugin'

	    class Media:
	        js = resolve_dependencies('myproject/js/admin/myplugin.js')

The attribute ``ring_plugin`` is required to name the Javascript's counterpart of our Python class.

If for instance, our ``MyCustomPlugin`` requires functionality to set a link, then instead of
replication the code required to set the link, we can rewrite our plugin as:

.. code-block:: python

	from cmsplugin_cascade.link.config import LinkPluginBase

	class MyCustomPlugin(LinkPluginBase):
	    ... other class attributes


Since ``LinkPluginBase`` provides it's own ``ring_plugin``, the corresponding Javascript code also
must inherit from this base class. Cascade handles this for you automatically, if the Javascript
code of the plugin is structured as:

.. code-block:: javascript

	django.jQuery(function($) {
	    'use strict';

	    var plugin_bases = eval(django.cascade.ring_plugin_bases.MyCustomPlugin);
	    django.cascade.MyCustomPlugin = ring.create(plugin_bases, {
	        constructor: function() {
	            this.$super();
	            // initialization code
	        },
	        custom_func: function() {
	            // custom functionality
	        }
	    });
	});

The important parts here is the call ``eval(django.cascade.ring_plugin_bases.MyCustomPlugin)``,
which creates the Javscript plugins our custom plugin inherits from.


.. _ring.js: http://ringjs.neoname.eu/
.. _media: https://docs.djangoproject.com/en/latest/topics/forms/media/
