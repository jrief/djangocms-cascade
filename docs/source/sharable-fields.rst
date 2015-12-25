============================
Working with sharable fields
============================

Sometime you'd want to remember sizes, links or any other options for rendering a plugin instance
across the project. In order to not have to do this job for each managed entity, you can remember
these settings using a name of your choice, controllable in a special section of the administration
backend.

Now, whenever someone adds a new instance using this plugin, a select box with these remembered
settings appears. He then can choose from one of the remembered settings, which frees him to
reenter all the values.


Configure a Cascade Plugins to optionally share some fields
===========================================================

Configuring a plugin to share specific fields with other plugins of the same type is very easy.
In the projects ``settings.py``, assure that ``'cmsplugin_cascade.sharable'`` is part of your
``INSTALLED_APPS``.

Then add a dictionary of Cascade plugins, with a list of fields which shall be sharable. For
example, with this settings, the image plugin can be configured to share its sizes and rendering
options among each other.

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'plugins_with_sharables': {
	        'BootstrapImagePlugin': ('image-shapes', 'image-width-responsive', 'image-width-fixed', 'image-height', 'resize-options',),
	    },
	    ...
	}


Control some named settings
===========================

Whenever a plugin is configured to allow to share fields, at the bottom of the plugin editor a
special field appears:

|remember-settings|

.. |remember-settings| image:: /_static/remember-settings.png

By activating the checkbox, adding an arbitrary name next to it and saving the plugin, an entity
of sharable fields is saved in the database. Now, whenever someone starts to edit a plugin of this
type, a select box appears on the top of the editor:

|use-shared-settings|

.. |use-shared-settings| image:: /_static/use-shared-settings.png

By choosing a previously named shared settings, the configured fields are disabled for input and
replaced by their shared field's counterparts.

In order to edit these shared fields in the administration backend, one must access 
**Home › Cmsplugin_cascade › Shared between Plugins**. By choosing a named shared setting, one can
enter into the shared field's editor. This editor auto adopts to the fields declared as shared,
hence will change from entity to entity. For the above example, it may look like this:

|edit-shared-fields|

.. |edit-shared-fields| image:: /_static/edit-shared-fields.png

In this editor one can change these shared settings globally, for all plugin instances where this
named shared settings have been applied to.
