djangocms-bootstrap
===================
A collection of plugins for DjangoCMS to add various HTML elements from the CSS framework
[Twitter Bootstrap](http://getbootstrap.com/2.3.2/) to CMS placeholders. This allows the editor of
a web page to manipulate the DOM, without having to edit HTML templates.

The **First Goal of this project** is to make available the full collection of widgets as documented
for the Bootstrap framework. With this plugin, then in many cases, **DjangoCMS** can be operated
with one single template. Such a template has to offer a generic placeholder for the main content of
each page.

The **Second Goal of this project** is to create an infrastructure which allows programmers to
easily add simple widget code, without having to implement an extra DjangoCMS plugin. This avoids
almost empty extra database tables.

For instance, implementing the Bootstrap Carousel, required only 17 lines of pure declaration code
and two simple templates.

Detailed documentation
----------------------
Find detailed documentation on [ReadTheDocs](http://djangocms-bootstrap.readthedocs.org/en/latest/).

Currently only Bootstrap version 2.3 is supported. As soon as AngularUI is available for Bootstrap
version 3, I will adopt the current code.

Build status
------------
[![Build Status](https://travis-ci.org/jrief/djangocms-bootstrap.png?branch=master)](https://travis-ci.org/jrief/djangocms-bootstrap)

Features
--------
* Use the **Bootstrap** scaffolding technique.
* Use **Bootstrap** buttons styles for your links.
* Insert **Boostrap Carousel** elements into the DOM.
* Insert the **Boostrap Hero** element into the DOM.
* Add thumbnails and images using highly customizable **Bootstraps** markup.
* Its very easy to integrate your own plugin, often with less than 10 lines of code.
* Well suited for developers running [Bootstrap with AngularJS](http://angular-ui.github.io/bootstrap/)
* Can easily be adopted for other CSS frameworks.

Example
-------
This shows the plugin editors to add a Bootstrap column container.

![Example](https://raw.github.com/jrief/djangocms-bootstrap/master/docs/source/_static/bootstrap-column-editor.png)

License
-------
Released under the terms of MIT License.

Copyright (C) 2013, Jacob Rief <jacob.rief@gmail.com>

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/jrief/djangocms-bootstrap/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

