.. render-template:

=======================================
Chose an alternative rendering template
=======================================

Sometimes you must render a plugin with a slightly different template, other than the given default.
A possible solution is to inherit from this template and override ``render_template``. This however
adds another plugin to the list of registered CMS plugins.

A simpler solution to solve this problem is to allow a plugin to be rendered with a template out of
a set of alternatives.


Change the path for template lookups
====================================

Some Bootstrap plugins are shipped with templates, which is optimized to be rendered by Angular-UI_
instead of the default. These alternative templates are located in the folder
``cascade/bootstrap3/angular-ui``. If your project uses AngularJS instead of jQuery, then configure
the lookup path in ``settings.py`` with

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'bootstrap3': {
	        ...
	        'template_basedir': 'angular-ui',
	    },
	}

This lookup path is applied only to the Plugin's field ``render_template`` prepared for it. Such a
template contains the placeholder ``{}``, which is expanded to the configured ``template_basedir``.


.. _Angular-UI: http://angular-ui.github.io/bootstrap/versioned-docs/0.13.4/

Configure a Cascade plugins to be rendered using alternative templates
======================================================================

All plugins which offer more than one rendering template, shall be added to the dictionary
``CMSPLUGIN_CASCADE['plugins_with_extra_render_templates']`` in your project's ``settings.py``.
Each value of this dictionary shall contain a list with two-tuples. The first element of this
two-tuple must be the templates filename, while the second element shall contain an arbitrary
name to identify that template.

Example:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'plugins_with_extra_render_templates': {
	        'TextLinkPlugin': (
	            ('cascade/link/text-link.html', _("default")),
	            ('cascade/link/text-link-linebreak.html', _("with linebreak")),
	        )
	    },
	    ...
	}


Usage
-----

When editing a **djangoCMS** plugins with alternative rendering templates, the plugin editor
adds a select box containing alternative rendering templates. Chose one other than the default,
and the plugin will be rendered using this other template.
