============================
Working with sharable fields
============================

Sometime you'd want to remember sizes and other options for rendering an image across the project.
In order to not have to do this jobs for each managed image, you can remember these settings using a
name of your choice and controllable in a special section of the administration backend.

Now, whenever someone adds a new instance using this plugin, a select box with these remembered
settings appears. He then can chose from one of the remembered settings, which frees him to
reenter all the values.

Moreover, by changing one of these remembered settings in the administration backend at
**Home › Cmsplugin_cascade › Shared between Plugins**, one can change the size and other options for
all images with these settings applied to them.


Configure a Cascade Plugins to optionally share some fields
===========================================================

Configuring a plugin to share specific fields with other plugins of the same type is very easy.
In the projects ``settings.py``, add a dictionary of Cascade plugins, with a list of fields which
shall be sharable. For example, with this settings, the image plugin can configured to share its
sizes and rendering options among each other.

.. code-block:: python

	CMSPLUGIN_CASCADE_WITH_SHARABLES = {
	    'BootstrapImagePlugin': ('image-shapes', 'image-width-responsive', 'image-width-fixed', 'image-height', 'resize-options',),
	}


Control some named settings
===========================
