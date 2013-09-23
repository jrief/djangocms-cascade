djangocms-bootstrap
===================

A Plugin for django CMS to add various HTML elements from the CSS framework “Twitter Bootstrap” to
other placeholders.


Installation
------------

This plugin requires `django CMS` 3.0 or higher to be properly installed.

* In your projects `virtualenv`_, run ``pip install djangocms-bootstrap``.
* Add ``'cmsplugin_bootstrap'`` to your ``INSTALLED_APPS`` settings, before the line ``cms``.
* Run ``manage.py migrate cmsplugin_bootstrap``.


Usage
-----

When adding plugins to a CMS placeholder, there is a section Bootstrap. In here you find some HTML
elements which are useful to modify the DOM tree.
adds a row container to the DOM::

  <div class="row"></div>

Add a column container to the DOM::

  <div class="spanX offsetY"></div>

The CSS classes can vary from span1 through span12. Additionally you may add 11 different offsets,
from offset1 though offset11.

For details on how to use the basic grid system, continue here: http://getbootstrap.com/2.3.2/scaffolding.html#gridSystem

A button wrapper for the LinkPlugin. Note that this does not add any HTML element. It rather offers
an additional context ``extra_classes`` to the child plugin, which can only be of kind LinkPlugin.
Therefore the template for the LinkPlugin has to be overridden by a slightly modified version.


Translations
------------

If you want to help translate the plugin please do it on transifex:

https://www.transifex.com/projects/p/django-cms/resource/djangocms-style/

