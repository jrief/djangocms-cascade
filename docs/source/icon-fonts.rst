.. _icon-fonts:

================
Using Icon Fonts
================

Introduction
============

Sometime we want to enrich our web pages with vectorized symbols. A lot of them can be found in
various font libraries, such as `Font Awesome`_, `Material Icons`_ and many more. A typical approach
would be to upload the chosen SVG symbol, and use it as image. This process however is time
consuming and error-prone to organize. Therefore, **djangocms-cascade** offers an utility in order
to work with icon fonts directly.

In order to setup a font, we currently must use Fontello_, an external service for icon font
generation. In the future, this service  might be integrated into **djangocms-cascade** itself.
In order to start, chose one or more icon fonts inside from the Fontello website and download the
generated webfont file to a local folder.


Uploading the Font
==================

In the Django backend, change into ``Start › django CMS Cascade › Uploaded Icon Fonts`` and add an
Icon Font object. Choose an appropriate name and upload the just downloaded webfont file, without
unzipping it. After the upload completed, all the imported icons appear grouped by their font
family. They now are ready for being used.


Using a Font Icon
=================

A font symbol can be used everywhere plain text can be added. Inside a **djangoCMS** placeholder
field add a plugin of type **Font Icon**. Select from one of the uploaded fonts. Now a list of
possible font icons appears. Select the desired icon, its size and its relative position in respect
of its wrapping element. After saving the form, that element should appear inside the chosen
container.


.. _Font Awesome: http://fontawesome.io/
.. _Material Icons: https://design.google.com/icons/
.. _Fontello: http://fontello.com/
