.. djangocms-cascade

Welcome to djangocms-cascade's documentation!
=============================================
**DjangoCMS-Cascade** is a collection of plugins for DjangoCMS >3.0 to add various HTML elements
from CSS frameworks, such as `Twitter Bootstrap`_ or the `960 Grid System`_ to the Django CMS
templatetag placeholder_. Currently Bootstrap-3.x is supported, but this module makes it
very easy to add other CSS frameworks or to extend an existing collection with additional elements.

**DjangoCMS-Cascade** allows web editors to layout their pages, without having to edit Django
templates. In most cases, one template with one single placeholder is enough. The editor then
can subdivide that placeholder into rows and columns, and add additional elements such as buttons,
rulers, or even the Bootstrap Carousel. Some basic understanding of the DOM_ and the grid system
from the chosen CSS framework is required though.

`Twitter Bootstrap`_ is a well documented CSS framework which gives web designers lots of
possibilities to add a consistent structure to their pages. This collection of DjangoCMS plugins
offers a subset of these predefined elements to web designers.

Project goals
-------------
#. Make available a meaningful subset of widgets as documented for the Bootstrap framework. With
   this module, then in many cases, **DjangoCMS** can be operated with one single template,
   containing a generic templatetag ``{% placeholder %}`` for the main content of each page.

#. Create a modular system, which allows programmers to add simple widget code, without having to
   implement an extra DjangoCMS plugin.

#. Allow to extend this DjangoCMS extension to be used with other CSS frameworks.

Contents:

.. toctree::

  installation
  usage
  scaffolding
  buttons
  thumbnails
  carousel
  navbar
  add_plugins
  history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Django: https://www.djangoproject.com/
.. _DjangoCMS: https://www.django-cms.org/
.. _Twitter Bootstrap: http://getbootstrap.com/
.. _960 Grid System: http://960.gs/
.. _placeholder: https://django-cms.readthedocs.org/en/latest/advanced/templatetags.html#placeholder
.. _DOM: http://www.w3.org/DOM/
.. _plugins: https://django-cms.readthedocs.org/en/latest/getting_started/plugin_reference.html
.. _Bootstrap grid system: http://getbootstrap.com/2.3.2/scaffolding.html#gridSystem
.. |column-editor| image:: _static/bootstrap-column-editor.png
    :width: 803
.. |pull-down| image:: _static/edit-plugins.png
    :width: 48
