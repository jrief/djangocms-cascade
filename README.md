djangocms-cascade
=================
**Update (2014-12-20):** Version 0.4.0 is about to be released soon. A lot of code changed last week, so be prepared if you update. This API change now hopefully is final. Please check [#49](https://github.com/jrief/djangocms-cascade/issues/49) for details.

**DjangoCMS-Cascade** Version 0.3.2 is the latest stable release. The upcoming new release is available under the 0.4.0 branch. It adds a huge amount of new features and has a much cleaner code base. If you start with **djangocms-cascade**, please start with the new branch.

Add DOM elements to a Django-CMS placeholder
---------------------------------------------
**DjangoCMS-Cascade** is a collection of plugins for DjangoCMS >3.0 to add various HTML elements
from CSS frameworks, such as [Twitter Bootstrap](http://getbootstrap.com/) or the
[960 Grid System](http://960.gs/) to any CMS
[placeholder](http://docs.django-cms.org/en/develop/getting_started/tutorial.html#creating-templates).
Currently **Bootstrap-3.x** and **960.gs** are supported, but this module makes it very easy to
add your preferred CSS frameworks. It is also very easy to extend an existing collection with
additional elements.

**DjangoCMS-Cascade** allows web editors to layout their pages, without having to edit Django
templates. In most cases, one template with one single placeholder is enough. The editor then
can subdivide that placeholder into rows and columns, and add additional elements such as buttons,
rulers, or even the Bootstrap Carousel.

Features
--------
* Use the scaffolding technique from the preferred CSS framework to subdivide a placeholder into a
  [grid system](http://getbootstrap.com/css/#grid).
* Make full usage of responsive techniques, by allowing
  [stacked to horizontal](http://getbootstrap.com/css/#grid-example-basic) classes per element.
* Use styled [buttons](http://getbootstrap.com/css/#buttons) to add links.
* Wrap special content into a [Jumbotron](http://getbootstrap.com/components/#jumbotron) or a
  [Carousel](http://getbootstrap.com/javascript/#carousel) 
* Add [thumbnails](http://getbootstrap.com/components/#thumbnails) and images in a responsive way.
* It is very easy to integrate additional elements from the preferred CSS framework, sometimes with
  less than 20 lines of code.
* Currenty **Bootstrap-3.x** and **960.gs** are supported, but other CSS frameworks can be easily
  added in a pluggable manner.

For instance, implementing the Bootstrap Carousel, required 50 lines of Python code and a simple
Django template.

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
it possible to implement a
[similar collection of plugins](https://github.com/jrief/djangocms-cascade/tree/bootstrap-2.3.2),
named **DjangoCMS-Bootstrap** and restricted to Twitter Bootstrap version 2.3.2.

In **DjangoCMS-Cascade**, this limitation also has been dropped, enabeling it to be used for every
kind of CSS framework - thus it has been renamed again. Additionally, the database model has been
reduced into one single field, which now stores all kind of arbitrary data and to be extensible in
a very flexible way.

License
-------
Released under the terms of MIT License.

Copyright (C) 2014, Jacob Rief <jacob.rief@gmail.com>
