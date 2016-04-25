.. _generic-plugins:

===============
Generic Plugins
===============


**Cascade** is shipped with a few plugins, which can be used independently of the underlying CSS
framework. To avoid duplication, they are bundled into the section **Generic** and are available
by default in the placeholders context menu.

All these plugins qualify as plugins with `extra fields`_, which means that they can be configured
by the site administrator to accept additional CSS styles and classes.


.. _extra fields: extra-fields

SimpleWrapperPlugin
===================

Use this plugin to add a wrapping element around a group of other plugins. Currently these HTML
elements can be used as wrapper: ``<div>``, ``<span>``, ``<section>``, ``<article>``. There is one
special wrapper named ``naked``. It embeds its children only logically, without actually embedding
them into any HTML element.


HorizontalRulePlugin
====================

This plugins adds a horizontal rule ``<hr>`` to the DOM. It is suggested to enable the
``margin-top`` and ``margin-bottom`` CSS styles, so that the ruler can be positioned
appropriately.


HeadingPlugin
=============

This plugins adds a text heading ``<h1>``...``<h6>`` to the DOM. Although simple headings can be
achieved with the **TextPlugin**, there they can't be styled using special CSS classes or styles.
Here the **HeadingPlugin** can be used, since any allowed CSS class or style can be added.


CustomSnippetPlugin
===================

Not every collection of DOM elements can be composed using the Cascade plugin system. Sometimes one
might want to add a simple HTML snippet. While it is be possible to create a plugin, rendering any
customized template yourself, an easier approach is to add that template to your ``settings.py``
via:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    # other settings
	    'plugins_with_extra_render_templates': {
	        'CustomSnippetPlugin': (
	            ('myproject/snippets/custom-template.html', "Custom Template Identifier"),
	            # other tuples
	        ),
	    },
	}

Now, when editing the page, a plugin named **Custom Snippet** appears in the *Generic* section of
the plugin dropdown menu. This plugin then offers a select element, where the site editor then can
chose between the configured templates.


Adding children to a CustomSnippetPlugin
----------------------------------------

It is even possible to add children to the **CustomSnippetPlugin**. Simple add these templatetag_s
to the customized template, and all plugins which are children of the **CustomSnippetPlugin** will
be rendered as well.

.. code-block:: django

	{% load cms_tags %}
	<wrapping-element>
	{% for plugin in instance.child_plugin_instances %}
	    {% render_plugin plugin %}
	{% endfor %}
	</wrapping-element>

.. _templatetag: https://docs.djangoproject.com/en/stable/ref/templates/language/#tags
