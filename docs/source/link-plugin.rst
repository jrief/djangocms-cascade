.. _link-plugin:

===========
Link Plugin
===========

**djangocms-cascade** ships with its own Link plugin. This is because other plugins from
**djangocms-cascade**, such as ButtonPlugin or PicturePlugin require the functionality to set links
to internal- and external URLs. The de-facto plugin for links, djangocms-link_ can't be used as a
base class for these plugins, therefore an alternative implementation had to be created. And as all
other Cascade plugins, this LinkPlugin also keeps its data in a JSON field.


Simple Link Plugin
==================

Before using this plugin, assure that ``'cmsplugin_cascade.link.simple'`` is member of the list or
tuple ``CMS_CASCADE_PLUGINS`` in the project's ``settings.py``.

|simple-link-element|

.. |simple-link-element| image:: _static/simple-link-element.png

The behavior of this Plugin is what you expect from a Link editor. By changing the Link type, one
can switch from a Link pointing to another page from this CMS, or point onto an external web page,
or point onto an email address.

The optional field **Title** can be used to add a ``title="some value"`` attribute to the
``<a href ...>`` element.

With **Link Target** one can specify, where the linked content shall appear. By default this is the
same windows as the current one.

Sharable Link Plugin
====================

Before using this plugin, assure that ``'cmsplugin_cascade.link.sharable'`` is a member of the list
or tuple ``CMS_CASCADE_PLUGINS`` in the project's ``settings.py``.

|sharable-link-element|

.. |sharable-link-element| image:: _static/sharable-link-element.png

The content of a sharable Link element can be shared with other Links of the same type. This can be
achieved by clicking on the checkbox *Remember these settings as: ...* and giving it a name of
your choice.

The next time your create a Link element, you may select a previously named settings from the select
field *Shared Settings*. Since these settings are shared among other plugins, they shall not be
changeable, and therefore all input fields are disabled.

Changing shared settings
------------------------

A shared plugin setting may be changed though, using the Django admin interface. Change into the
list view for **Shared between Plugins** and select the named shared settings.

Extending the Link Plugin
=========================


.. _djangocms-link: https://github.com/divio/djangocms-link
