=======================================
Customize CSS classes and inline styles
=======================================

Plugins shipped with **djangocms-cascade** offer a basic set of CSS classes as declared by the
chosen CSS framework. These offered classes normally do not fulfill the requirements for real world
sites. This is specially true, if you extend your site with one of the many available
`Bootstrap themes`_.

While **djangocms-cascade** is easily expendable, it would be overkill to re-implement the available
plugins, just to add an extra field for a customized CSS class or an extra inline style. For that
purpose, one can add a set of potential CSS classes and potential CSS inline styles for Cascade
plugins, enabled for this feature. Moreover, this feature can be adopted individually on a per-site
base.

.. _Bootstrap themes: https://themes.getbootstrap.com/


.. extra-fields:

Configure a Cascade plugins to accept extra fields
==================================================

It is possible to configure each plugin to accept an additional ID tag, one ore more CSS classes or
some inline styles. By default the plugins: BootstrapButtonPlugin, BootstrapRowPlugin,
BootstrapJumbotronPlugin and the SimpleWrapperPlugin are eligible for accepting extra styles.
Additionally, by default the user can override the margins of the HeadingPlugin and the
HorizontalRulePlugin.

To override these defaults, first assure that ``'cmsplugin_cascade.extra_fields'`` is part of
your ``INSTALLED_APPS``. Then add a dictionary of Cascade plugins, which shall be extendible
to the project's ``settings.py``, for instance:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'plugins_with_extra_fields': {
	        'BootstrapButtonPlugin': PluginExtraFieldsConfig(),
	        'BootstrapRowPlugin': PluginExtraFieldsConfig(),
	        'BootstrapJumbotronPlugin': PluginExtraFieldsConfig(inline_styles={
	            'extra_fields:Paddings': ['padding-top', 'padding-bottom'],
	            'extra_units:Paddings': 'px,em'}),
	        'SimpleWrapperPlugin': PluginExtraFieldsConfig(),
	        'HeadingPlugin': PluginExtraFieldsConfig(inline_styles={
	            'extra_fields:Paddings': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
	            'extra_units:Paddings': 'px,em'}, allow_override=False),
	        'HorizontalRulePlugin': PluginExtraFieldsConfig(inline_styles={
	            'extra_fields:Paddings': ['margin-top', 'margin-bottom'],
	            'extra_units:Paddings': 'px,em'}, allow_override=False),
	    },
	    ...
	}

Here the class ``PluginExtraFieldsConfig`` is used to fine-tune which extra fields can be
set while editing the plugin. Assigning that class without arguments to a plugin, allows us to
specify the extra fields using the Django administration backend at:

*Home › django CMS Cascade › Custom CSS classes and styles*

Here the site administrator can specify for each concrete plugin, which extra CSS classes, ID tags
and extra inline styles shall be used.

If we use ``PluginExtraFieldsConfig(allow_override=False)``, then the site administrator *can not*
override the configuration using the backend. Then every extra field must be specified by the
configuration directive:

.. autoclass:: cmsplugin_cascade.extra_fields.config.PluginExtraFieldsConfig
   :members:


Enable extra fields through the administration backend
======================================================

To enable this feature, in the administration backend navigate to

*Home › django CMS Cascade › Custom CSS classes and styles*  and click onto the button named
**Add Custom CSS classes styles**.

From the field named "Plugin Name", select one of the available plugins, for example
**Bootstrap Simple Wrapper**. Then, from the field named "Site", select the site where those extra
styles shall be applied.

|customize-styles|

.. |customize-styles| image:: /_static/customize-styles.png

If the plugin has the default configuration, for example: sets the upper, lower, upper, and lower margins.
The default settings above will be available in the plug-in editor because CMSPLUGIN_CASCADE variable.
**merge_extra_fields**: True are set in defaults.


Allow ID
--------

With "Allow id tag" enabled, an extra field will appear on the named plugin editor. There a user
can add any arbitrary name which will be rendered as ``id="any_name"`` for the corresponding plugin
instance.

Allowing ID's is specially useful for the **Heading Plugin**, so the Links can point directly to
that ID (bookmark linking).


CSS classes
-----------

In the field named "CSS class names", the administrator may specify arbitrary CSS classes separated
by commas. One of these CSS classes then can be added to the corresponding Cascade plugin. If
more than one CSS class shall be addable concurrently, activate the checkbox named "Allow multiple".


CSS inline styles
-----------------

The administrator may activate all kinds of CSS inline styles by clicking on the named checkbox. For
settings describing distances, additionally specify the allowed units to be used.

If a user opens the corresponding plugin inside the **Structure View**, he will see an extra select
field to choose the CSS class and some input fields to enter say, extra margins, heights or
whatever has been activated.


Use it rarely, use it wise
..........................

Adding too many styling fields to a plugin can mess up any web project. Therefore be advised to use
this feature rarely and wise. If many people have write access to plugins, set extra permissions on
this table, in order to not mess things up. For instance, it rarely makes sense to activate
``min-width``, ``width`` and ``max-width``.


Dynamically add styles to the Text-Editor
=========================================

In Cascade it is also possible to dynamically add styles to the CKTextEditor.
Ensure that in your ``settings.py`` the following is active:

.. python

	CKEDITOR_SETTINGS = {
	    ...
	    'toolbar_CMS': [
	        ...
	        ['Styles'],
	        ...
	    ],
	    'stylesSet': format_lazy('default:{}', reverse_lazy('admin:cascade_texteditor_config')),
	}

Then in the Django-Admin, by adding entries in *Start › django CMS Cascade › Text Editor Configs*
it is possible to use these special styles inside the text editor.
