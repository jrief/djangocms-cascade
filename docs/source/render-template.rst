.. render-template:

=======================================
Chose an alternative rendering template
=======================================

Sometimes you must render a plugin with a slightly different template, other than the given default.
A possible solution is to inherit from this template and override ``render_template``. This however
adds another plugin to the list of registered CMS plugins.

A simpler solution to solve this problem is to allow a plugin to be rendered with a template out of
a set of alternatives.


Configure a Cascade plugins to be rendered using alternative templates
======================================================================

The **SegmentationPlugin** must be activated separately on top of other **djangocms-cascade**
plugins. In ``settings.py``, add to

All plugins which offer more than one rendering template, shall be added to the dictionary
``CMSPLUGIN_CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES`` in your project's ``settings.py``.
Each value of this dictionary shall contain a list with two-tuples. The first element of this
two-tuple must be the templates filename, while the second element shall contain an arbitrary
name to identify that template.

Example:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS_WITH_EXTRA_RENDER_TEMPLATES = {
	    'TextLinkPlugin': (
	        ('cascade/link/textlink.html', _("default")),
	        ('cascade/link/textlink-linebreak.html', _("with linebreak")),
	    )
	}

Usage
=====

When editing a **djangoCMS** plugins with alternative rendering templates, the plugin editor
adds a select box containing alternative rendering templates. Chose one other than the default,
and the plugin will be rendered using another template.
