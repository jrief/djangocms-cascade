.. _client-side:

========================
Handling the client side
========================

**DjangoCMS-Cascade** is shipped with a lot of plugins, all having their own inheritance hierarchy.
Due to the flexibility of Cascade, this inheritance hierarchy can be extended though some
configuration settings, while bootstrapping the runtime environment. Some plugins for instance, can
be configured to store some settings in a common data store. This in the admin backend requires a
special Javascript plugin, from which the client side must inherit as well.

Hence on the client side, we would like to describe the same inheritance hierarchy using Javascript.
Therefore Cascade is equipped with a small, but very powerful library named ring.js_. It makes
Javascript behave almost like Python. If a Cascade plugin provides a Javascript counterpart,
then other Cascade plugins inheriting from the former one, map their inheritance hierarchy in
Javascript exactly as provided by the plugins written in Python.


Implementing the client
=======================

Say, we want to add some client side code to a Cascade plugin. We first must import that Javascript
file through Django's `static asset definitions`_ using the ``Media`` class, or if you prefer in a
dynamic property method ``media()``.

At some point during the initialization, Cascade must call the constructor of the Javascript
plugin we just added. Therefore Cascade plugins provide an extra attribute named ``ring_plugin``,
which is required to name the Javascript's counterpart of our Python class. You can use any name
you want, but it is good practice to use the same name as the plugin.

The Python class of our custom Cascade plugin then might look like:

.. code-block:: python

	from cmsplugin_cascade.plugin_base import CascadePluginBase

	class MyCustomPlugin(CascadePluginBase):
	    name = "Custom Plugin"
	    ... other class attributes
	    ring_plugin = 'MyCustomPlugin'

	    class Media:
	        js = ['mycustomproject/js/admin/mycustomplugin.js']

whereas it's Javascript counterpart might look like:

.. code-block:: javascript
	:caption: mycustomproject/js/admin/mycustomplugin.js

	django.jQuery(function($) {
	    'use strict';

	    django.cascade.MyCustomPlugin = ring.create({
	        constructor: function() {
	            // initialization code
	        },
	        custom_func: function() {
	            // custom functionality
	        }
	    });
	});


After yours, and all other Cascade plugins have been initialized in the browser, the Cascade
framework invokes ``new django.cascade.MyCustomPlugin();`` to call the constructor function.


Plugin Inheritance
==================

If for instance, our ``MyCustomPlugin`` requires functionality to set a link, then instead of
replication the code required to handle the link input fields, we can rewrite our plugin as:

.. code-block:: python

	from cmsplugin_cascade.link.config import LinkPluginBase

	class MyCustomPlugin(LinkPluginBase):
	    ... class attributes as in the previous example

Since ``LinkPluginBase`` provides it's own ``ring_plugin`` attribute, the corresponding Javascript
code *also must inherit* from that base class. Cascade handles this for you automatically, if the
Javascript code of the plugin is structured as:

.. code-block:: javascript
	:caption: mycustomproject/js/admin/mycustomplugin.js

	django.jQuery(function($) {
	    'use strict';

	    var plugin_bases = eval(django.cascade.ring_plugin_bases.MyCustomPlugin);

	    django.cascade.MyCustomPlugin = ring.create(plugin_bases, {
	        constructor: function() {
	            this.$super();
	            // initialization code
	        },
	        ...
	    });
	});

The important parts here is the call to ``eval(django.cascade.ring_plugin_bases.MyCustomPlugin)``,
which resolves the Javascript functions our custom plugin inherits from.


.. note:: In case you forgot to add a missing Javascript requirement, then ring.js complains that
	it can't access the attribute of ``__classId__`` of undefined. If you run into this problem,
	recheck that all Javascript files have been loaded and initialized in the correct order.


.. _ring.js: http://ringjs.neoname.eu/
.. _static asset definitions: https://docs.djangoproject.com/en/stable/topics/forms/media/
