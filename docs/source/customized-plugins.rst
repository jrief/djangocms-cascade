.. customized-plugins:

=================
Extending Cascade
=================

All Cascade plugins are derived from the same base class ``CascadeModelBase``, which stores all its
model fields inside a dictionary, serialized as JSON string in the database. This makes it much
easier to extend the Cascade eco-system, since no database migration is required when adding a new,
or extending plugins from this project.

The database model ``CascadeModelBase`` stores all the plugin settings in a single JSON field named
``glossary``. This in practice behaves like a Django context, but in order to avoid confusion with
the latter, it has been named “glossary”.


Simple Example
==============

This plugin is very simple and just renders static content which has been declared in the template.

.. code-block:: python

	from cms.plugin_pool import plugin_pool
	from cmsplugin_cascade.plugin_base import CascadePluginBase
	
	class StylishPlugin(CascadePluginBase):
	    name = 'Stylish Element'
	    render_template = 'cms/bootstrap3/stylish-element.html'
	
	plugin_pool.register_plugin(StylishPlugin)

If the editor form pops up for this plugin, a dumb message appears: “There are no further settings
for this plugin”. This is because no editable fields have been added to that plugin yet.


Customize Stored Data
=====================

In order to make the plugin remember its settings and other optional data, the programmer must add
a list of special form fields to its plugin. These fields then are used to auto-generate the editor
for this DjangoCMS plugin.

Each of those form fields handle a special field value, or in some cases, a list of field values.
They all require a widget, which is used when rendering the editors form.

Lets add a simple selector to choose between a red and a green color. Do this by adding a
``PartialFormField`` to a member list named ``glossary_fields``.

.. code-block:: python

	from django.forms import widgets
	from cmsplugin_cascade.plugin_base import CascadePluginBase, PartialFormField
	
	class StylishPlugin(CascadePluginBase):
	    ...
	    glossary_fields = [
	        PartialFormField('color',
	            widgets.Select(choices=(('red', 'Red'), ('green', 'Green'),)),
	            label="Element's Color",
	            initial='red',
	            help_text="Specify the color of the DOM element."
	        ),
	        # more PartialFormField objects
	    ]

In the plugin's editor, the form now pops up with a single select box, where the user can choose
between a *red* and a *green* element.

A ``PartialFormField`` accepts five arguments:

* The name of the field. It must be unique in the given list of ``glossary_fields``.
* The widget. This can be a built-in Django widget or any valid widget derived from it.
* The ``label`` used to describe the field. If omitted, the ``name`` of the partial form field is used.
* An optional ``initial`` value to be used with Radio- or Select fields.
* An optional ``help_text`` to describe the field's purpose.


Widgets for a Partial Form Field
================================

For single text fields or select boxes, Django's built-in widgets, such as ``widgets.TextInput``
or ``widgets.RadioSelect`` can be used. Sometimes these simple widgets are not enough, therefore
some special input widgets have been prepared to be used with **DjangoCMS-Cascade**. They are all
part of the module ``cmsplugin_cascade.widgets``.

:MultipleTextInputWidget:
	Use this widget to group a list of text input fields together. This for instance is used, to
	encapsulate all inline styles into one JSON object.

:NumberInputWidget:
	The same as Django's ``TextInput``-widget, but doing field validation. This checks if the
	entered input data is a valid number.

:MultipleInlineStylesWidget:
	The same as the ``MultipleTextInputWidget``, but doing field validation. This checks if the
	entered input data ends with ``px`` or ``em``.


Overriding the Form
===================

For the plugin editor, **djangocms-cascade** automatically creates a form for each
``PartialFormField`` in the list of ``glossary_fields``. Sometimes however, you might need more
control over the fields displayed in the editor, versus the fields stored inside the ``glossary``.

Similar to the Django's ``admin.ModelAdmin``, this can be achieved by overriding the plugins form
element. Such a customized form can add as many fields as required, while the controlled glossary
contains a compact summary.

To override the plugins form, add a member ``form`` to your plugin. This member variable shall refer
to a customized form derived from ``forms.models.ModelForm``. For further details about how to use
this feature, refer to the supplied implementations.


Plugin Attribute Reference
==========================

``CascadePluginBase`` is derived from ``CMSPluginBase``, so all `CMSPluginBase attributes`_ can
also be overridden by plugins derived from ``CascadePluginBase``. Please refer to their
documentation for details.

Additionally ``BootstrapPluginBase`` allows the following attributes:

:name:
	This name is shown in the pull down menu in structure view. There is not default value.

:tag_type:
	Default: ``div``.

	A HTML element into which this plugin is wrapped. If ``tag_type`` is ``None``, then the plugin
	is 	considered as “naked” and rendered without a wrapping DOM element. This for instance is
	useful to render the ``<a>`` element as button, using styling classes.

:require_parent:
	Default: ``True``. This differs from ``CMSPluginBase``.

	Is it required that this plugin is a child of another plugin? Otherwise the plugin can be added
	to any placeholder.

:parent_classes:
	Default: None.

	A list of Plugin Class Names. If this is set, the plugin may only be added to plugins listed
	here.

:allow_children:
	Default: ``True``. This differs from ``CMSPluginBase``.

	Can this plugin have child plugins? Or can other plugins be placed inside this plugin?

:child_classes:
	Default: A list of plugins, which are allowed as children of this plugin. This differs from
	``CMSPluginBase``, where this attribute is None.

	Do not override this attribute. **DjangoCMS-Cascade** automatically generates a list of allowed
	children plugins, by evaluating the list ``parent_classes`` from the other plugins in the pool.

	Plugins, which are part of the plugin pool, but which do not specify their parents using the
	list ``parent_classes``, may be added as children to the current plugin by adding them to the
	attribute ``generic_child_classes``.

:generic_child_classes:
	Default: None.

	A list of plugins which shall be added as children to a plugin, but which themselves do not
	declare this plugin in their ``parent_classes``.

:glossary_fields:
	Default: None

	A list of ``PartialFormField``'s. See the documentation above for details.

:default_css_class:
	Default: None.

	A CSS class which is always added to the wrapping DOM element.

:default_inline_styles:
	Default: None.

	A dictionary of inline styles, which is always added to the wrapping DOM element.

:get_identifier:
	This is a classmethod, which can be added to a plugin to give it a meaningful name.

	Its signature is::

	    @classmethod
	    def get_identifier(cls, obj):
	        return 'A plugin name'

	This method shall be used to name the plugin in structured view.

:form:
	Override the form used by the plugin editor. This must be a class derived from
	``forms.models.ModelForm``.


.. _CMSPluginBase attributes: https://django-cms.readthedocs.org/en/develop/extending_cms/custom_plugins.html#plugin-attribute-reference
