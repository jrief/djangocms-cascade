.. customized-styles:

=======================================
Customize CSS classes and inline styles
=======================================

Plugins shipped with **djangocms-cascade** offer a basic set of CSS classes as prepared by the
chosen CSS framework. For real world sites, these offered classes normally are far too little.

While **djangocms-cascade** is easily extendible, it would be overkill to re-implement the available
plugins, just to add an extra field for a customized CSS class or an extra inline style. For that
purpose, one can add a set of potential CSS classes and potential CSS inline styles for Cascade
plugins, enabled for this feature.


Manage extra fields
===================

To enable this feature, navigate to **Home › Cmsplugin_cascade › Custom CSS classes and styles**
in the administration backend and click onto the **Add Custom CSS classes styles** button.

From the field named “Plugin Name”, select **Bootstrap Simple Wrapper**. From the fields named
“Site”, select the current site.

|customize-styles|

.. |customize-styles| image:: /_static/customize-styles.png

In the field named “CSS class names” you may specify arbitrary CSS classes separated by commas.
One of these CSS classes then can be added to the Cascade plugin **Bootstrap Simple Wrapper**. If
more than one class shall be addable, activate the checkbox named “Allow multiple”.

Additionally you may activate all kinds of CSS inline styles by clicking on the named checkbox. For
settings describing distances, additionally specify the allowed units to be used.

Now, if you choose a "Simple Wrapper Plugin" inside the Structure View, you will see an extra 
select field to chose the CSS class and some input fields to enter extra margins, paddings or
whatever has been activated.

Use it rarely, use it wise
--------------------------

Adding too many styling fields to a plugin can mess up any web project. Therefore be advised to use
this feature rarely and wise. If many people have write access to plugins, set extra permissions on
this table, in order to not mess things up. For instance, it rarely makes sense to activate
``min-width``, ``width`` and ``max-width``.


Programming Cascade plugins with extra fields
=============================================

Enabling a plugin to allow any extra CSS class or inline style is very easy and straight forward.
Simple add a mixin class to your existing plugin:

.. code-block:: python

	from cmsplugin_cascade.plugin_base import BootstrapPluginBase
	from cmsplugin_cascade.mixins import ExtraFieldsMixin
	
	class MySpecialPlugin(ExtraFieldsMixin, BootstrapPluginBase):
	    name = _("My special Plugin")
	    # other members as usual

If you override the classmethods ``get_css_classes`` and ``get_inline_styles`` ensure that you
call its super-method and hand through its returned values.
