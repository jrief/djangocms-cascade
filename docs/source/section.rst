.. section:

=================
Section Bookmarks
=================

If you have a long page, and you want to allow the visitors of your site to quickly navigate to
different sections, then you can use bookmarks and create links to the different sections of any
HTML page.

When a user clicks on a bookmark link, then that page will load as usual but will scroll immediately,
so that the bookmark is at the very top of the page. Bookmarks are also known as anchors. They can
be added to any HTML element using the attribute ``id``. For example:

.. code-block:: html

	<section id="unique-identifier-for-that-page">

For obvious reasons, this identifier must be unambiguous, otherwise the browser does not know
where to jump to. Therefore **djangocms-cascade** enforces the uniqueness of all bookmarks used on
each CMS page.


Configuration
=============

The HTML standard allows the usage of the ``id`` attribute on any element, but in practice it only
makes sense on ``<section>``, ``<article>`` and the various heading elements. Cascade by default is
configured to allow bookmarks on the **SimpleWrapperPlugin** and the **HeadingPlugin**. This can
be overridden in the project's configuration settings using:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'plugins_with_bookmark': [list-of-plugins],
	    ...
	}


Hashbang Mode
-------------

Links onto bookmarks do not work properly in hashbang mode. Depending on the HTML settings, you may
have to prefix them with ``/`` or ``!``. Therefore **djangocms-cascade** offers a configuration
directive:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'bookmark_prefix': '/',
	    ...
	}

which automatically prefixes the used bookmark.


Usage
=====

When editing a plugin that is eligible for adding a bookmark, an extra input field is shown:

|section-bookmark|

.. |section-bookmark| image:: /_static/section-bookmark.png

You may add any identifier to this field, as long as it is unique on that page. Otherwise the form
will be rejected when saving.


Hyperlinking to a bookmark
==========================

When editing a **TextLink**, **BootstrapButton** or the link fields inside the **Image** or
**Picture** plugins, the user gets an additional drop-down menu to choose one of the bookmarks for
the given page. This additional drop-down is only available if the **Link** is of type *CMS page*.

|link-bookmark|

.. |link-bookmark| image:: /_static/link-bookmark.png

If no bookmarks have been associated with the chosen CMS page, the drop-down menu displays only
*Page root*, which is the default.
