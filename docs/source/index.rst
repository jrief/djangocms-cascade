.. djangocms-cascade:

Welcome to DjangoCMS-Cascade's documentation
============================================

Project's home
--------------

Check for the latest release of this project on Github_.

Please report bugs or ask questions using the `Issue Tracker`_.

In **djangoCMS-Cascade** version 0.7.0, the configuration settings have been hugely refactored.
If you were using version 0.6.2 or lower, check your ``settings.py`` for deprecated configuration
directives.


Project's goals
---------------

#. Create a modular system, which allows programmers to add simple widget code, without having to
   implement an extra djangoCMS_ plugins for each of them.

#. Make available a meaningful subset of widgets as available for the most common CSS frameworks,
   such as `Twitter Bootstrap`_. With these special plugins, in many configurations, **djangoCMS**
   can be operated using one single template, containing one generic placeholder.

#. Extend this **djangoCMS** plugin, to be used with other CSS frameworks such as `Foundation 5`_,
   Unsemantic_ and others.

#. Use the base functionality of **djangoCMS-Cascade** to easily add special plugins. For instance,
   djangoSHOP_ implements all its cart and checkout specific forms this way.


Contents:
---------

.. toctree::

  impatient
  introduction
  installation
  link-plugin
  bootstrap3/grid
  bootstrap3/image-picture
  bootstrap3/navbar
  bootstrap3/other-components
  segmentation
  sharable-fields
  customize-styles
  customized-plugins
  generic-plugins
  changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Github: https://github.com/jrief/djangocms-cascade
.. _Issue Tracker: https://github.com/jrief/djangocms-cascade/issues
.. _djangoCMS: https://www.django-cms.org/
.. _djangoSHOP: https://www.django-shop.org/
.. _Twitter Bootstrap: http://getbootstrap.com/
.. _Foundation 5: http://foundation.zurb.com/
.. _Grid System 960: http://960.gs/
.. _Unsemantic: http://unsemantic.com/
