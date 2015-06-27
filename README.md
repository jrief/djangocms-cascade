# djangocms-cascade
**DjangoCMS-Cascade** is the Swiss army knife for working with Django CMS plugins.


## Add DOM elements to a Django-CMS placeholder

**DjangoCMS-Cascade** is a collection of plugins for DjangoCMS >= 3.0.8 to add various HTML elements to any CMS
[placeholder](http://docs.django-cms.org/en/develop/getting_started/tutorial.html#creating-templates) in a hierarchical tree.

It allows web editors to layout their pages, without having to edit Django templates. In most cases,
one template with one single placeholder is enough. The editor then can subdivide that placeholder
into rows and columns, and add additional elements such as buttons, rulers, and much more.

Currently about a dozen compontents from **Bootstrap-3.x** are avialble, but **Cascade** makes it very easy
to add additional compontents, often with less than 20 lines of Python code and without any database migrations.

Since all plugins share the same database table, it is very easy to build inheritance trees. For instance,
Cascade's own ``LinkPlugin`` inherits from a ``LinkPluginBase``, which also is the parent of the ``ImagePlugin``
and the ``ButtonPlugin``. This helps to share the common functionality required for linking.


### Its pluggable

**DjangoCMS-Cascade** is very modular, keeping its CMS modules in functional groups. These groups have to be
activated independently in your ``settings.py``. It also is possible to activate only certain Plugins out
of a group. One such group is ``cmsplugin_cascade.bootstrap3``, but it could be replaced by a future
**Bootstrap-4**, the **Foundation**, **YUI** or whatever other CSS framework you prefer.


### Configurable individually

Each Cascade Plugin can be styled individually. The site-administrator can specify which CSS styles and CSS
classes can be added to each plugin. Then the page-editor can pick one of the allowed styles to adopt his
elements accordingly.


### Reuse your data

Each Cascade Plugin can be configured by the site-administrator to share some or all of its data fields.
This for instance is handy, to keep references onto external URLs in a central place. Or is can be used
to resize all images sharing a cetrain property in one go.


### Segment the DOM

It is even possible to group plugins into seperate evaluation contexts. This for instance is used to render
different Plugins, depending on whether a user is authenticated or anonymous.



## News for next major release 0.5.0

* Tested with **django-cms 3.0.13** and Django-1.6.
* Added SegmentationPlugin. This allows to conditionally render parts of the DOM, depending on
  the status of various ``request`` object members, such as ``user``.
* Setting ``CASCADE_LEAF_PLUGINS`` has been replaced by ``CMSPLUGIN_CASCADE_ALIEN_PLUGINS``. This simplifies
  the programming of third party plugins, since the author of a plugin now only must set the member
  ``alien_child_classes = True``.


Help needed
-----------

If you like this project, please invest some time and test it with Django-1.7/1.8, django-cms-3.1
and if possible Python-3.4.

With migrations added to Django-1.7, testing and developing plugins for django-cms get really messy.
I currently have no resources to do all this cross-development.

Travis-CI worked for djangocms-cascade, Django-1.7 and django-cms-3.0.12, but since the last upgrade
this is not the case anymore. If someone can find out why, it would be really great.


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
* Use segmentation the render parts of the DOM conditionally.
* It is very easy to integrate additional elements from the preferred CSS framework. For instance,
  implementing the Bootstrap Carousel, required 50 lines of Python code and two simple Django templates.
* Since all the data is stored in JSON, no database migration is required if a field is added, modified
  or removed from the plugin.
* Currently **Bootstrap-3.x** is supported, but other CSS frameworks can be easily added in a pluggable manner.

In addition to easily implement any kind of plugin, **DjangoCMS-Cascade** makes it possible to add
reusable helpers. Such a helper enriches a plugin with an additional, configurable functionality:

* By making some of the plugin fields sharable, one can reuse these values for other plugins of the
  same kind. This for instance is handy for the image and picture plugin, so that images always are
  resized to predefined values.
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

In **DjangoCMS-Cascade** since version 0.4, the code base has been hugely refactored. If you where
using version 0.3.2 upgrade carefully, since the API changed. Please contact me directly in case you
need help to migrate your projects.


License
-------

Released under the terms of MIT License.

Copyright &copy; 2015, Jacob Rief <jacob.rief@gmail.com>
