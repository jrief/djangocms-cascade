.. _changelog:

===============
Release History
===============

0.8.5.dev0
----------

0.8.4
-----

* Fixed a regression in "Restore from clipboard".
* Fixed TextLinkPlugin to work again as child of TextPlugin.
* ContainerPlugin can only be added below a placeholder.
* Prepared demo to work with Django-1.10.
* Plugins marked as "transparent" are only allowed as parents,
  if they allow children.

0.8.3
-----

* Added ``CustomSnippetPlugin``. It allows to add arbitrary custom templates to the project.
* Fixed #160: Error copying Carousel plugin
* Plugins marked as "transparent" can be parents of everybody.
* BootstrapPanelPlugin now accepts inline CSS styles.


0.8.2
-----

* Cascade does not create migrations for proxy models anymore. This created major problems if
  Cascade components have been switched on and off. All existing migrations of proxy models have
  been removed from the migration files.
* Fixed: Response of more than one entry on non unique clipboards.
* Added :class:`cmsplugin_cascade.models.SortableInlineCascadeElement` which can be used for
  keeping sorted inline elements.
* :class:`cmsplugin_cascade.bootstrap3.gallery.BootstrapGalleryPlugin` can sort its images.

0.8.1
-----
* Hotfix: removed invalid dependency in migration 0007.

0.8.0
-----
* Compatible with Django-1.9
* Fixed #133: BootstrapPanelPlugin now supports custom CSS classes.
* Fixed #132: Carousel Slide plugin with different form.
* Fixed migration problems for proxy models outside Cascade.
* Replaced SelectMultiple against CheckboxSelectMultiple in admin for extra fields.
* Removed SegmentationAdmin from admin backend.
* Disallow whitespace in CSS attributes.
* Require django-reversion 1.10.1 or newer.
* Require django-polymorphic 0.9.1 or newer.
* Require django-filer 1.1.1 or newer.
* Require django-treebeard 4.0 or newer.
* Require django-sekizai 0.9.0 or newer.


0.7.3
-----
* Use the outer width for fluid containers. This allows us to add images and carousels which extend
  the the browser's edges.
* Fixed #132: Carousel Slide plugin different form.
* Fixed #133: BootstrapPanelPlugin does not support custom CSS classes.
* Fixed #134: More plugins can be children of the ``SimpleWrapperPlugin``. This allows us to be more
  flexible when building the DOM tree.
* ``BootstrapContainerPlugin`` now by default accepts extra inline styles and CSS classes.

0.7.2
-----
* Add a possibility to prefix Cascade plugins with a symbol of your choice, to avoid confusion
  if the same name has been used by another plugin.
* All Bootstrap plugins can override their templates globally though a configuration settings
  variable. Usefule to switch between jQuery and AngularJS versions of a widget.
* Added TabSet and TabPanel plugins.
* It is possible to persist the content of the clipboard in the database, retrieve and export
  it as JSON to be reimported on an unrelated site.

0.7.1
-----
* Added a **HeadingPlugin** to add single text headings independently of the HTML TextEditorPlugin.

0.7.0
-----
Cleanup release, removing a lot of legacy code. This adds some incompatibilities to previous
versions:

* Instead of half o dozen of configuration directives, now one Python dict is used. Therefore
  check your ``settings.py`` for configurations starting with ``CMSPLUGIN_CASCADE_...``.
* Tested with **Django-1.8**. Support for version 1.7 and lower has been dropped.
* Tested with **djangoCMS** version 3.2. Support for version 3.0 and lower has been dropped.
* Tested with **django-select2** version 5.2. Support for version 4 has been dropped.
* The demo project now uses SASS instead of plain CSS, but SASS is not a requirement during normal
  development.

0.6.2
-----
* In Segment: A condition raising a TemplateSyntaxError now renders that error inside a HTML
  comment. This is useful for debugging non working conditions.
* In Segment: An alternative AdminModel to UserAdmin, using a callable instead of a model field,
  now works.
* In Segment: It is possible to use ``segmentation_list_display = (list-of-fields)`` in an
  alternative AdminModel, to override the list view, when emulating a user.

0.6.1
-----
* Added a panel plugin to support the Bootstrap Panel.
* Added experimental support for secondary menus.
* Renamed ``AccordionPlugin`` to ``BootstrapAccordionPlugin`` for consistency and to avoid future
  naming conflicts.

0.6.0
-----
* Fixed #79: The column width is not reduced in width, if a smaller column precedes a column for a
  smaller displays.
* Fixed: Added extra space before left prefix in buttons.
* Enhanced: Access the link content through the glossary's ``link_content``.
* New: Plugins now can be rendered using an alternative template, choosable through the plugin
  editor.
* Fixed in SegmentationPlugin: When overriding the context, this updated context was only used for
  the immediate child of segment. Now the overridden context is applied to all children and
  grandchildren.
* Changed in SegmentationPlugin: When searching for siblings, use a list index instead of
  ``get_children().get(position=...)``.
* Added unit tests for SegmentationPlugin.
* Added support for **django-reversion**.
* By using the setting ``CMSPLUGIN_CASCADE_LINKPLUGIN_CLASSES``, one can replace the class
  ``LinkPluginBase`` by an alternative implementation.
* When using *Extra Styles* distances now can have negative values.
* In caption field of ``CarouselSlidePlugin`` it now is possible to set links onto arbitrary pages.

**Possible backwards incompatibility**:

* For consistency with naming conventions on other plugins, renamed ``cascade/plugins/link.html``
  -> ``cascade/link/link-base.html``. **Check your templates**!
* The setting ``CMSPLUGIN_CASCADE_SEGMENTATION_MIXINS`` now is a list of two-tuples, where the first
  declares the plugin's model mixin, while the second declares the model admin mixin.
* Removed from setting: ``CMSPLUGIN_CASCADE_BOOTSTRAP3_TEMPLATE_DIR``. The rendering template now 
  can be specified during runtime.
* Refactored and moved ``SimpleWrapperPlugin`` and ``HorizontalRulePlugin`` from
  ``cmsplugin_cascade/bootstrap3/`` into ``cmsplugin_cascade/generic/``. The glossary field
  ``element_tag`` has been renamed to ``tag_type``.
* Refactored ``LinkPluginBase`` so that external implementations can create their own version,
  which then is used as base for TextLinkPlugin, ImagePlugin and PicturePlugin.
* Renamed: ``PanelGroupPlugin`` -> ``Accordion``, ``PanelPlugin`` -> ``AccordionPanelPlugin``,
  because the Bootstrap project renamed them back to their well known names.

0.5.0
-----
* Added SegmentationPlugin. This allows to conditionally render parts of the DOM, depending on
  the status of various ``request`` object members, such as ``user``.
* Setting ``CASCADE_LEAF_PLUGINS`` has been replaced by ``CMSPLUGIN_CASCADE_ALIEN_PLUGINS``. This simplifies
  the programming of third party plugins, since the author of a plugin now only must set the member
  ``alien_child_classes = True``.

0.4.5
-----
* Fixed: If no breakpoints are set, don't delete widths and offsets from the glossary, as otherwise
  this information is lost.
* Fixed broken import for ``PageSelectFormField`` when not using **django_select2**.
* Admin form for ``PluginExtraFields`` now is created on the fly. This fixes a rare circular
  dependency issue, when accessing ``plugin_pool.get_all_plugins()``.

0.4.4
-----
* Removed hard coded input fields for styling margins from **BootstrapButtonPlugin**, since
  it is possible to add them through the **Extra Fields** dialog box.
* [Column ordering](http://getbootstrap.com/css/#grid-column-ordering) using ``col-xx-push-n``
  and ``col-xx-pull-n`` has been added.
* Fixed: Media file ``linkplugin.js`` was missing for **BootstrapButtonPlugin**.
* Hard coded configuration option ``EXTRA_INLINE_STYLES`` can now be overridden by the projects
  settings


0.4.3
-----
* The templatetag ``bootstrap3_tags`` and the templates to build Boostrap3 styled menus,
  breadcrumbs and paginator, have been moved into their own repository
  at https://github.com/jrief/djangocms-bootstrap3.
* `Column ordering`_ using ``col-xx-push-n`` and ``col-xx-pull-n`` has been added.

.. _Column ordering: http://getbootstrap.com/css/#grid-column-ordering

0.4.2
-----
* Fixed: Allow empty setting for CMSPLUGIN_CASCADE_PLUGINS
* Fixed: Use str(..) instead of b'' in combination with from __future__ import unicode_literals

0.4.1
-----
* Fixed: Exception when saving a ContainerPlugin with only one breakpoint.
* The ``required`` flag on a field for an inherited LinkPlugin is set to False for shared settings.
* Fixed: Client side code for disabling shared settings did not work.

0.4.0
-----
* Renamed ``context`` from model ``CascadeElement`` to ``glossary`. The identifier ``context`` lead
  to too much confusion, since it is used all way long in other CMS plugins, where it has a
  complete different meaning.
* Renamed ``partial_fields`` in all plugins to ``glossary_fields``, since that's the model field
  where they keep their information.
* Huge refactoring of the code base, allowing a lot of more features.

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
