.. _bootstrap_buttons:

Bootstrap Buttons
=================

`Bootstrap button`_ styles can be applied to the well known DjangoCMS LinkPlugin_. In order to use
it, create a **Bootstrap > Button wrapper** plugin and add as child a LinkPlugin. Now, these two
nested plugins will display links as if they were Bootstrap buttons.

Button wrapper
--------------
This plugin is, as its name says a wrapper for the LinkPlugin. This means that you can not add any
other kind of plugin to this wrapper. It offers four configuration settings:

* An optional button size.
* An optional button color.
* A checkbox to specify, if the target link shall be hidden.
* Margins to the neighbor elements in CSS units (``px`` or ``em``).

Check the `Bootstrap button`_ documentation for details about these classes.

.. note:: Bootstrap adds special button classes the HTML tag ``<a>``. The current template shipped
   with the LinkPlugin can not render these additional classes. This template therefore has been
   overridden and can be found in ``templates/cms/plugins/link.html``.

.. _LinkPlugin: https://django-cms.readthedocs.org/en/develop/getting_started/plugin_reference.html#link
.. _Bootstrap button: http://getbootstrap.com/2.3.2/base-css.html#buttons
