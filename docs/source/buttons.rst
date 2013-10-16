.. _bootstrap_buttons:

Bootstrap Buttons
=================

`Bootstrap button`_ styles can be applied to the well known DjangoCMS LinkPlugin_. In order to use
it, create a **Bootstrap > Button** plugin and add as child a LinkPlugin. Now, these two nested
plugins will display links using the Bootstrap's button classes.

.. note:: Bootstrap adds special button classes the HTML tag ``<a>``. The current template shipped
   with the LinkPlugin can not render these additional classes. This template therefore has been
   overridden and can be found in ``templates/cms/plugins/link.html``.

.. _LinkPlugin: https://django-cms.readthedocs.org/en/develop/getting_started/plugin_reference.html#link
.. _Bootstrap button: http://getbootstrap.com/2.3.2/base-css.html#buttons
