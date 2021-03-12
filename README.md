# djangocms-cascade

[![Build Status](https://travis-ci.org/jrief/djangocms-cascade.png?branch=master)](https://travis-ci.org/jrief/djangocms-cascade)
[![Python versions](https://img.shields.io/pypi/pyversions/djangocms-cascade.svg)](https://pypi.python.org/pypi/djangocms-cascade)
[![Software license](https://img.shields.io/pypi/l/djangocms-cascade.svg)](https://github.com/jrief/djangocms-cascade/blob/master/LICENSE-MIT)
[![Gitter chat room](https://badges.gitter.im/jrief/djangocms-cascade.svg)](https://gitter.im/awesto/djangocms-cascade)
[![Latest version on PyPI](https://img.shields.io/pypi/v/djangocms-cascade.svg)](https://pypi.python.org/pypi/djangocms-cascade)

The Swiss army knife for working with Django-CMS plugins.

## Why Use DjangoCMS-Cascade?

**DjangoCMS-Cascade** is a collection of plugins for Django-CMS
[placeholders](http://docs.django-cms.org/en/latest/introduction/templates_placeholders.html#templates-placeholders).
Instead of creating one database model for each CMS plugin, Cascade shares one database model for
all of them. The payload then is stored inside a JSON field instead of declaring each attribute
explicitly. This furthermore prevents us to handle all kind of nasty database migration problems.


## Version 2.0 (released 2021-02-02)

**Version 2.0 only supports Django versions 3.1 and higher.**

Backward compatibility had to be dropped, because version 2.0 now fully supports the native internal
`JSONField` as offered by Django version 3.1. It hence is not possible to run a version of Cascade
which can switch between those field types.

From a functional point of view, there is no difference to version 1.3.7.

After upgrading, run `./manage.py migrate cmsplugin_cascade`. It will rewrite the field type of
all `JSONField`s to Django's internal `JSONField` without modifying its content. For safety reasons,
it is highly recommended to backup the database before migrating. 


## Features

### Perfect for nested grid systems

Since **Cascade** keeps track on the widths of all columns, ``<img>`` and ``<picture>`` elements can
be rendered in a responsive way, so that the browser only loads the image required for the visible
viewport.


### Extend plugins with additional features

Using a JSON field to store the payload gives us much more flexibility. We can for instance enrich
our plugins with additional attributes, configured during runtime. This can be used to optionally
share attributes across different plugins (referenced by an alias name), add CSS classes and styles,
or offer alternative rendering templates.


### Set links onto your own views

Another nice aspect of this approach is, that we can override the functionality used to set links
onto pages which are not part of the CMS. This is specially useful, since we do not want to
re-implement this functionality for all plugins, which require links, ie. images, pictures,
buttons and text-links.


### Copy content and paste it somewhere else

Since the payload of plugins is already serialized, we can even copy them from one site to another
site supporting **djangocms-cascade**.


## Documentation

Find detailed documentation on [ReadTheDocs](http://djangocms-cascade.readthedocs.io/en/latest/).

Please see the [Release Notes](http://djangocms-cascade.readthedocs.io/en/latest/changelog.html)
before upgrading from an older version.


## Architecture

### It's pluggable

**DjangoCMS-Cascade** is very modular, keeping its CMS modules in functional groups. These groups
have to be activated independently in the project's `settings.py`. It also is possible to activate only
certain plugins out of a group. Currently there are two such groups, `cmsplugin_cascade.bootstrap3` and
`cmsplugin_cascade.bootstrap4`, but this list could be extended by say, **Foundation**,
**Angular Material** or whatever other CSS framework you prefer.


### Configurable individually

Each **Cascade** plugin can be styled individually. The site-administrator can specify which CSS
styles and CSS classes can be added to each plugin. Then the page-editor can pick one of the allowed
styles to adopt his elements accordingly.


### Reuse your data

Each **Cascade** plugin can be configured by the site-administrator to share some or all of its data
fields. This for instance is handy, to keep references onto external URLs in a central place. Or is
can be used to resize all images sharing a cetrain property in one go.


### Segment the DOM

It is even possible to group plugins into seperate evaluation contexts. This for instance is used to
render different Plugins, depending on whether a user is authenticated or anonymous.


### Responsive Images

In modern web development, images must adopt to the column width in which they are rendered.
Therefore the ``<img ...>`` tag, in addition to the well known ``src`` attribute, also accepts
additional ``srcset``'s, one for each media query. Here **djangocms-cascade** calculates the
required widths for each image, depending on the current column layout considering all media
breakpoints.

This is also implemented for the ``<picture>`` element with all of it's children, normally
``<source srcset="...">``.

It also supports resolutions of more than one physical pixel per logical pixel as found in Retina
displays.


### Other Features

* Use the scaffolding technique from the preferred CSS framework to subdivide a placeholder into a
  [grid system](http://getbootstrap.com/css/#grid).
* Make full usage of responsive techniques, by allowing
  [stacked to horizontal](http://getbootstrap.com/css/#grid-example-basic) classes per element.
* Use styled [buttons](http://getbootstrap.com/css/#buttons) to add links.
* Wrap special content into a [Jumbotron](http://getbootstrap.com/components/#jumbotron) or a
  [Carousel](http://getbootstrap.com/javascript/#carousel).
* Add ``<img>`` and ``<picture>`` elements in a responsive way, so that more than one image URL
  points onto the resized sources, one for each viewport using the ``srcset`` tags or the
  ``<source>`` elements.
* Use segmentation to conditionally render parts of the DOM.
* Temporarily hide a plugin to show up in the DOM.
* Upload an self composed font from [Fontello](http://fontello.com/) and use it's icon in plain text
  or as framed eye catchers.
* It is very easy to integrate additional elements from the preferred CSS framework. For instance,
  implementing the Bootstrap Carousel, requires only 50 lines of Python code and two simple Django
  templates.
* Since all the data is stored in JSON, no database migration is required if a field is added,
  modified or removed from the plugin.
* Currently **Bootstrap-3** and **Bootstrap-4** is supported, but other CSS frameworks can be
  easily added in a pluggable manner.
* It follows the "batteries included" philosophy, but still remains very modular.

In addition to easily implement any kind of plugin, **DjangoCMS-Cascade** makes it possible to add
reusable helpers. Such a helper enriches a plugin with an additional, configurable functionality:

* By making some of the plugin fields sharable, one can reuse these values for other plugins of the
  same kind. This for instance is handy for the image and picture plugin, so that images always are
  resized to predefined values.
* By allowing extra fields, one can add an optional ``id`` tag, CSS classes and inline styles. This
  is configurable on a plugin and site base.
* It is possible to customize the rendering templates shipped with the plugins.
* Since all data is JSON, you can dump the content of one placeholder and insert it into another one,
  even on a foreign site. This for instance is useful to transfer pages from the staging site to production.


### Help needed

If someone wants to start a subproject for a CSS framework, other than Bootstrap-3/4.

If you are a native English speaker, please check the documentation for spelling mistakes and
grammar, since English is not my mother tongue.
