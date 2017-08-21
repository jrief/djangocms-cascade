.. _hide-plugins:

==============================
Conditionally hide some plugin
==============================

Sometimes a placholder contains some plugins, which temporarily should not show up while rendering.
If this feature is enabled, then instead of deleting them, it is possible to hide them.


Enable the meachanism
=====================

In the projects ``settings.py``, add:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'allow_plugin_hiding': True,
	    ...
	}

By default, this feature is disabled. If enabled, **djangocms-cascade** adds a checkbox to every
plugin editor. This checkbox is labeled *Hide plugin*. If checked, the plugin and all of it's
children are not rendered in the current tree. To easily distinguish hidden plugins in structure
mode, they are rendered using a shaded background.
