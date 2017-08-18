.. _minions:

==============================
Use Cascade outside of the CMS
==============================

One of the most legitimate points **djangocms-cascade** can be criticised for, is the lack of
static content rendering. Specially in projects, where we want to work with static pages instead
of CMS pages, one might fall back to handcrafting HTML, giving up all the benefits of rapid
prototyping as provided by the Cascade plugin system.

Since version 0.14 of **djangocms-cascade** one can prototype the page content and export it as
JSON file using :ref:clipboard. Later on, one can reuse that persisted data and create the same
content outside of a CMS page. This is specially useful, if you must persist the page content
in the projects version control system.


Usage
=====

After filling the placeholder of a CMS page, using the plugins from **djangocms-cascade**
go to the context menu of the placeholder and click *Copy all*.

Next, inside Django's administration backend, go to

	Home › django CMS Cascade › Persited Clipboard Content

and *Add Persisted Clipboard Content*. Now the *Data* field will be filled with a cascade
of plugins serialized as JSON data. Copy that data and paste it into a file locatable by Django's
static file finders.


In Templates
============

Create a Django template, where instead of adding a Django-CMS placeholder, use the templatetag
``render_cascade``. Example:

.. code-block:: Django

	{% load cascade_tags %}

	{% render_cascade "myapp/mycontent.json" %}

This templatetag now renders the content just as if it would be rendered by the CMS. This means
that changing the template of a **djangocms-cascade** plugin, immediatly has effect on the rendered
output. This is so to say **Model View Control**, where the Model is the content peristed as JSON,
and the View is the template provided by the plugin. It separates the composition of HTML components
from their actual representation, allowing a much better division of work during the page creation.


Caveats when creating your own Plugins
======================================

When developing your own plugins, consider the following precautions:


Invoking ``super``
------------------

Instead of invoking ``super(MyPlugin, self).some_method()`` use
``self.super(MyPlugin, self).some_method()``. This because **djangocms-cascade** creates a
list of "shadow" plugins, which do not inherit from ``CMSPluginBase``.


Templatetag ``render_plugin``
-----------------------------

Django-CMS provides a templatetag ``render_plugin``. Don't use it in templates provided by
**djangocms-cascade** plugins. Instead use the templatetag named ``render_plugin`` from
Cascade. Example:

.. code-block:: Django

	{% load cascade_tags %}
	<div class="some-css-class">
	{% for plugin in instance.child_plugin_instances %}
	    {% render_plugin plugin %}
	{% endfor %}
	<div>
