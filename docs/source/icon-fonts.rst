======================
Using Fonts with Icons
======================

Introduction
============

Sometime we want to enrich our web pages with vectorized symbols. A lot of them can be found in
various font libraries, such as `Font Awesome`_, `Material Icons`_ and many more. A typical approach
would be to upload the chosen SVG symbol, and use it as image. This process however is time
consuming and error-prone to organize. Therefore, **djangocms-cascade** offers an optional submodule,
so that we can work with externally packed icon fonts.

In order to use such a font, currently we must use Fontello_, an external service for icon font
generation. In the future, this service  might be integrated into **djangocms-cascade** itself.


Configuration
-------------

To enable this service in **djangocms-cascade**, in ``settings.py`` add:

.. code-block:: python

	INSTALLED_APPS = [
	    ...
	    'cmsplugin_cascade',
	    'cmsplugin_cascade.icon',
	    ...
	]

	CMSPLUGIN_CASCADE_PLUGINS = [
	    ...
	    'cmsplugin_cascade.icon',
	    ...
	]

This submodule, can of course be combined with all other submodules available for the Cascade
ecosystem.

If ``CMS_PLACEHOLDER_CONF`` is used to configure available plugins for each placeholder, assure
that the ``TextIconPlugin`` is added to the list of ``text_only_plugins``.

Since the CKEditor widget must load the font stylesheets for it's own WYSIWIG mode, we have to add
this special setting to our configuration:

.. code-block:: python

	from django.core.urlresolvers import reverse_lazy
	from cmsplugin_cascade.utils import format_lazy

	CKEDITOR_SETTINGS = {
	    ...
	    'stylesSet': format_lazy(reverse_lazy('admin:cascade_texticon_wysiwig_config')),
	}


Uploading the Font
==================

In order to start with an external font icon, choose one or more icons and/or whole font families
from the Fontello_ website and download the generated webfont file to a local folder.

In Django's admin backend, change into ``Start › django CMS Cascade › Uploaded Icon Fonts`` and
add an Icon Font object. Choose an appropriate name and upload the just downloaded webfont file,
without unzipping it. After the upload completed, all the imported icons appear grouped by their
font family name. They now are ready for being used by the Icon plugin.


Using the Icon Plugin
=====================

A font symbol can be used everywhere plain text can be added. Inside a **django-CMS** placeholder
field add a plugin of type **Icon**. Select a family from one of the uploaded fonts. Now a list of
possible symbols appears. Choose the desired symbol, its size and color. Optionally choose a
background color, the relative position in respect of its wrapping element and a border width with
style and color. After saving the form, that element should appear inside the chosen container.

It is good practice to only use one uploaded icon font per site. If you forgot a symbol, go back
to the Fontello_ site and recreate your icon font. Then replace that icon font by uploading it
again.

.. warning:: If you use more than one font on the same page, please assure that Fontello assigns
	unique glyph codes to all of the symbols – this usually is not the case. Otherwise, the
	glyph codes will collapse, and the visual result is not what you expect.


Shared Settings
---------------

By default, the **IconPlugin** is configured to allow to share the following styling attributes:

* Icon size
* Icon color
* Background color, or without background
* Text alignment
* Border width, color and style
* Border radius

By storing these attributes under a common name, one can reuse them across various icons, without
having to set them for each one, separately. Additionally, each of the shared styling attributes
can be changed globally in Django's admin backend at
``Start › django CMS Cascade › Shared between Plugins``. For details please refer to the section
about :doc:`sharable-fields`.


Using the Icon Plugin in plain text
===================================

If **django-CMS** is configured to use the **djangocms-ckeditor-widget**, then you may use the
**Icon Plugin** inside plain text. Place the cursor at the desired location in text and select
**Icon** from the pull down menu **CMS Plugins**. This opens a popup where you may select the
font family and the symbol. All other attributes described above, are not available with this
type of plugin.

.. _Font Awesome: http://fontawesome.io/
.. _Material Icons: https://design.google.com/icons/
.. _Fontello: http://fontello.com/
