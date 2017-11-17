==============================
Use Cascade outside of the CMS
==============================

One of the most legitimate points **djangocms-cascade** can be criticised for, is the lack of
static content rendering. Specially in projects, where we want to work with static pages instead
of CMS pages, one might fall back to handcrafting HTML, giving up all the benefits of rapid
prototyping as provided by the Cascade plugin system.

Since version 0.14 of **djangocms-cascade**, one can prototype the page content and export it as
JSON file using :doc:`clipboard`. Later on, one can reuse that persisted data and create the same
content outside of a CMS page. This is specially useful, if you must persist the page content
in the project's version control system.


Usage
=====

After the placeholder of a CMS page, is filled up with plugins from **djangocms-cascade**,
switch into *Structure Mode*, go to the context menu of that placeholder and click *Copy all*.

Next, inside Django's administration backend, go to

	Home › Django CMS Cascade › Persited Clipboard Content

and click onto *Add Persisted Clipboard Content*. The *Data* field will now be filled with a
cascade of plugins serialized as JSON data. Copy that data and paste it into a file locatable
by Django's static file finders, for example ``myproject/static/myapp/cascades/slug.json``.


In Templates
============

Create a Django template, where instead of adding a Django-CMS placeholder, use the templatetag
``render_cascade``. Example:

.. code-block:: Django

	{% load cascade_tags %}

	{% render_cascade "myapp/cascades/slug.json" %}

This templatetag now renders the content just as if it would be rendered by the CMS. This means
that changing the template of a **djangocms-cascade** plugin, immediately has effect on the rendered
output. This is so to say **Model View Control**, where the Model is the content peristed as JSON,
and the View is the template provided by the plugin. It separates the composition of HTML components
from their actual representation, allowing a much better division of work during the page creation.


Caveats when creating your own Plugins
======================================

When developing your own plugins, consider the following precautions:


Invoking ``super``
------------------

Instead of invoking ``super(MyPlugin, self).some_method()`` use
``self.super(MyPlugin, self).some_method()``. This is required because **djangocms-cascade**
creates a list of "shadow" plugins, which do not inherit from ``CMSPluginBase``.


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


Caching
=======

Even though rendering using this templatetag is slightly faster than the classic ``placeholder``
tag provided by the CMS (because we don't hit the database for each plugin instance), combining
each plugin template with its context also takes its time. Therefore plugins rendered by
``render_cascade``, by default are cached as well, just as their CMS counterparts.

This caching is disabled for plugins containing the attribute ``cache = False``. It can be turned
off globally using the directive ``CMSPLUGIN_CASCADE['cache_strides'] = True`` in the project's
``settings.py``.
