djangocms-cascade
=================
**DjangoCMS-Cascade** is a collection of plugins for DjangoCMS >3.0 to add various HTML elements
from CSS frameworks, such as [Twitter Bootstrap](http://getbootstrap.com/) or the
[960 Grid System](http://960.gs/) to any CMS
[placeholder](http://docs.django-cms.org/en/develop/getting_started/tutorial.html#creating-templates).
Currently Bootstrap-3.x is supported, but this module makes it very easy to add other CSS frameworks
or to extend an existing collection with additional elements.

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
* Other CSS frameworks can easy be added in a pluggable manner.

For instance, implementing the Bootstrap Carousel, required 50 lines of Python code and a simple
Django template.

Detailed documentation
----------------------
Find detailed documentation on [ReadTheDocs](http://djangocms-cascade.readthedocs.org/en/latest/).

Build status
------------
[![Build Status](https://travis-ci.org/jrief/djangocms-cascade.png?branch=master)](https://travis-ci.org/jrief/djangocms-cascade)

The **First Goal of this project** is to make available the full collection of widgets as documented
for the Bootstrap framework. With this plugin, then in many cases, **DjangoCMS** can be operated
with one single template. Such a template has to offer a generic placeholder for the main content of
each page.

The **Second Goal of this project** is to create an infrastructure which allows programmers to
easily add simple widget code, without having to implement an extra DjangoCMS plugin. This avoids
almost empty extra database tables.

Example
-------
This shows the plugin editors to add a Bootstrap column container.

![Example](https://raw.github.com/jrief/djangocms-bootstrap/master/docs/source/_static/bootstrap-column-editor.png)

History
-------
This project started as a simple [wrapper](https://github.com/jrief/cmsplugin-text-wrapper) for the
DjangoCMS TextPlugin, so that text elements could be shifted horizontally using the Grid System 960. 

DjangoCMS starting with version 3.0, allows to nest plugins inside other plugins. This feature made
it possible to implement a [similar collection of plugins](https://github.com/jrief/djangocms-bootstrap),
restricted however for Twitter Bootstrap version 2.3.2.

With **DjangoCMS-Cascade**, this limitation also has been dropped, enabeling it to be used for every
kind of CSS framework - thus it has been renamed again. Additionally, the database model has been
reduced into one single field, which now stores all kind of arbitrary data.

License
-------
Released under the terms of MIT License.

Copyright (C) 2014, Jacob Rief <jacob.rief@gmail.com>

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/jrief/djangocms-bootstrap/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
