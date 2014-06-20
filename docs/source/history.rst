.. _release_history:

===============
Release History
===============
0.4.0
-----
* Renamed ``context`` from model ``CascadeElement`` to ``glossary`. The identifier ``context`` lead
  to too much confusion, since it is used all way long in other CMS plugins, where it has a
  complete different meaning.

0.3.2
-----
* Fixed: Missing unicode conversion for method ``get_identifier()``
* Fixed: Exception handler for form validation used ``getattr`` incorrectly.

0.3.1
-----
* Added compatibility layer for Python-3.3.

0.3.0
-----
* Complete rewrite. Now offers elements for Bootstrap 3 and other CSS frameworks.

0.2.0
-----
* Added carousel.

0.1.2
-----
* Fixed: Added missign migration.

0.1.1
-----
* Added unit tests.

0.1.0
-----
* First published revision.

Thanks
======

This DjangoCMS plugin originally was derived from https://github.com/divio/djangocms-style, so the
honor for the idea of this software goes to Divio and specially to Patrick Lauber, aka digi604.

However, since my use case is different, I removed all the existing code and replaced it against
something more generic suitable to add a collection of highly configurable plugins.
