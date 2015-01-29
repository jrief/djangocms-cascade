djangocms-cascade
=================
**DjangoCMS-Cascade** is the Swiss army knife for working with Django CMS plugins.

Add DOM elements to a Django-CMS placeholder
---------------------------------------------
**DjangoCMS-Cascade** is a collection of plugins for DjangoCMS >= 3.0.8 to add various HTML elements
from CSS frameworks, such as [Twitter Bootstrap](http://getbootstrap.com/) or the
[960 Grid System](http://960.gs/) (discontinued) to any CMS
[placeholder](http://docs.django-cms.org/en/develop/getting_started/tutorial.html#creating-templates).
Currently **Bootstrap-3.x** and **960.gs** (discontinued) are supported, but this module makes
it very easy to add your preferred CSS frameworks. It is also very easy to extend an existing
collection with additional elements.

**DjangoCMS-Cascade** allows web editors to layout their pages, without having to edit Django
templates. In most cases, one template with one single placeholder is enough. The editor then
can subdivide that placeholder into rows and columns, and add additional elements such as buttons,
rulers, or even the Bootstrap Carousel.

News
----
Starting with version 0.4.3, the templatetag ``bootstrap3_tags`` and the templates to build 
Boostrap3 styled menus, breadcrumbs and paginator, have been moved into their own repository
named [djangocms-bootstrap3](https://github.com/jrief/djangocms-bootstrap3).

Features
--------
* Use the scaffolding technique from the preferred CSS framework to subdivide a placeholder into a
  [grid system](http://getbootstrap.com/css/#grid).
* Make full usage of responsive techniques, by allowing
  [stacked to horizontal](http://getbootstrap.com/css/#grid-example-basic) classes per element.
* Use styled [buttons](http://getbootstrap.com/css/#buttons) to add links.
* Wrap special content into a [Jumbotron](http://getbootstrap.com/components/#jumbotron) or a
  [Carousel](http://getbootstrap.com/javascript/#carousel) 
* Add ``<img>`` and ``<picture>`` elements in a responsive way, so that more than one image URL
  point onto the resized sources, one for each viewport using the ``srcset`` tags or the ``<source>``
  elements.
* It is very easy to integrate additional elements from the preferred CSS framework. For instance,
  implementing the Bootstrap Carousel, required 50 lines of Python code and two simple Django templates.
* Since all the data is stored in JSON, no database migration is required if a field is added, modified
  or removed from the plugin.
* Currenty **Bootstrap-3.x** is supported, but other CSS frameworks can be easily added in a pluggable manner.

In addition to easily implement any kind of plugin, **DjangoCMS-Cascade** makes it possible to add
reusable helpers. Such a helper enriches a plugin with an additional, configurable functionality:

* By making some of the plugin fields sharable, one can reuse these values for other plugins. This for
  instance is handy for the image and picture plugin, so that images always are resized to predefined
  values.
* By allowing extra fields, one can add an optional ``id`` tag, CSS classes and inline styles. This
  is configurable on a plugin and site base.

Detailed documentation
----------------------
Find detailed documentation on [ReadTheDocs](http://djangocms-cascade.readthedocs.org/en/latest/).

Build status
------------
[![Build Status](https://travis-ci.org/jrief/djangocms-cascade.png?branch=master)](https://travis-ci.org/jrief/djangocms-cascade)

History
-------
This project started as a simple [wrapper](https://github.com/jrief/cmsplugin-text-wrapper) for the
DjangoCMS TextPlugin, so that text elements could be shifted horizontally using the Grid System 960. 

DjangoCMS starting with version 3.0, allows to nest plugins inside other plugins. This feature made
it possible to implement this kind of plugin.

In **DjangoCMS-Cascade** version 0.4.0, the code base has been hugely refactored. If you where using
version 0.3.2 upgrade carefully, since the API changed. Please contact me directly in case you
need help to migrate your projects.

License
-------
Released under the terms of MIT License.

Copyright &copy; 2014, Jacob Rief <jacob.rief@gmail.com>
