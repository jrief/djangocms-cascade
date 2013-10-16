.. _add_bootstrap_plugins:

Add Bootstrap plugins
=====================
Since all Bootstrap plugins are derived from the same base class, there is no need to add an
additional table to the database, when you add your own plugin to this project. The database model
instead used three JSON fields which can handle arbitrary data. This makes it very easy to add new 
plugins to this project.

Here is a very basic example::

  from cms.plugin_pool import plugin_pool
  from cmsplugin_bootstrap.plugin_base import BootstrapPluginBase
  
  
  class MyBootstrapPlugin(BootstrapPluginBase):
      name = 'My plugin'
      render_template = "cms/plugins/bootstrap/my-plugin.html"
      tag_type = 'div'
      css_class_choices = # list of tuples
      extra_classes_widget = # a widget
      tagged_classes_widget = # a widget
      extra_styles_widget = # a widget
  
  plugin_pool.register_plugin(ButtonWrapperPlugin)


Plugin Attributes
-----------------
``BootstrapPluginBase`` is derived from ``CMSPluginBase``, so all `CMSPluginBase attributes`_ can
be overridden here. Check the documentation for details.

Additionally ``BootstrapPluginBase`` allows the following attributes. The default is ``None``, so if
you don't specify them, they won't show up in the plugin editor.

:name:
  This name is shown in the pull down menu.

:tag_type: 
  A HTML element into which this plugin is wrapped. The special tag_type ``naked`` specifies
  a plugin without wrapping HTML code.

:css_class_choices:
  This is a list of 2-tuples containing the main class to be added to the HTML tag of this plugin
  element. In the editor a pull down menu is rendered to choose from this list.

:extra_classes_widget:
  Use a ``MultipleRadioButtonsWidget`` to create this widget. In the plugin editor is renders a list
  of separate radio button groups.
  
  To construct a ``MultipleRadioButtonsWidget``, pass in a list or tuple. This list (or tuple) shall
  contain another tuple, where the first value is a unqiue identifier for this radio button group.
  The second value shall be a list of 2-tuples containing the choices. The first value of this
  2-tuple is the class to be rendered in the frontend. The second value is the label nearby each
  radio button in the plugin editor.

:tagged_classes_widget:
  Use a ``MultipleCheckboxesWidget`` to create this widget. In the plugin editor is renders a list
  of checkboxes.
  
  To construct a ``MultipleCheckboxesWidget``, pass in a list or tuple of 2-tuples. These 2-tuples
  contain the choices which may exclusively be turned on or off. The first value of this 2-tuple is
  the class to be rendered in the frontend. The second value is the label nearby each checkbox
  button in the plugin editor. 

:extra_styles_widget:
  Use a ``ExtraStylesWidget`` to create this widget.  In the plugin editor is renders a list of
  input fields, where the user can add extra CSS values.
  
  To construct an ``ExtraStylesWidget``, pass in a list or tuple of strings. These strings contain
  the CSS attributes to be used for adding extra styles to the HTML tag in the frontend.

.. _CMSPluginBase attributes: https://django-cms.readthedocs.org/en/develop/extending_cms/custom_plugins.html#plugin-attribute-reference