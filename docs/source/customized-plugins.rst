.. customized-plugins:

Add Customized Plugins
======================
Since all Bootstrap plugins are derived from the same base class ``CascadeModelBase``, there rarely
is a need to create or extend a database model, when adding customized plugins to a project. The
database model ``CascadeModelBase`` stores all the plugin settings in a single JSON field named
``glossary``. This makes it very easy to add new plugins or extend existing ones for this project.

Simple Example
--------------
``stylish_plugin.py``::

	from cms.plugin_pool import plugin_pool
	from cmsplugin_cascade.plugin_base import CascadePluginBase
	
	class StylishPlugin(CascadePluginBase):
	    name = 'Stylish Element'
	    render_template = 'cms/bootstrap3/stylish-element.html'
	
	plugin_pool.register_plugin(StylishPlugin)

This plugin is very simple and just renders static content which has been declared in the template.
Thus, if the editor form pops up, a dumb message appears, telling that “There are no further
settings for this plugin”.

Customize Stored Data
---------------------
In order to make the plugin remember its settings and other optional data, one must add a list of
special form fields to this plugin. These fields then are used to build the editor for this
DjangoCMS plugin.

editing
models

to the plugin, handling a partial part of the model associated with the plugin. Each of those form
fields handles a special field value, or in some cases a list of field values. They all require a
widget, which is used while rendering the editors form.

This list of partial form fields is added to the plugin as::

	from django.forms import widgets
	from cmsplugin_cascade.plugin_base import CascadePluginBase, PartialFormField
	
	class StylishPlugin(CascadePluginBase):
	    ...
	    glossary_fields = [
	        PartialFormField('color',
	            widgets.Select(choices=(('red', 'Red'), ('green', 'Green'),)),
	            label="Element's Color", initial='red',
	            help_text="Specify the color of the DOM element."
	        ),
	        # more PartialFormField objects
	    ]

In the plugin's editor, now the form pops up with a single select box, where the user can choose
between red and green elements.

A ``PartialFormField`` accepts five arguments:

* The name of the field. It must be unique in the given list of ``glossary_fields``.
* The widget. This can be a built-in Django widget or any valid widget derived from it.
* The ``label`` used to describe the field. If omitted, the ``name`` of the partial form field is used.
* An optional ``initial`` value to be used with Radio- or Select fields.
* A ``help_text`` to describe the field's purpose.

Widgets for a Partial Form Field
--------------------------------
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

Plugin Attribute Reference
--------------------------
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

.. _CMSPluginBase attributes: https://django-cms.readthedocs.org/en/develop/extending_cms/custom_plugins.html#plugin-attribute-reference
