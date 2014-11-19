=======================
HTML5 <picture> element
=======================

Bootstrap's responsive grid system, helps developers to adapt their site layout to a wide range of
devices, from smart-phones to large displays. This works fine as long as the content can adopt to
the different widths. Adding the CSS class ``img-responsive`` to an ``<img ... />`` tag, resizes
that image to fit into the surrounding column. However, since images are delivered by the server
in one specific size, they either are too small and must be upscaled, resulting in an grainy image,
or are too big, resulting in a waste of bandwidth and slowing down the user experience, when surfing
over a 3G network.

Adaptive resizing the images
============================

An obvious idea would be to let the server decide, which image resolution fits best to the browsing
device. This however is bad practice. Images are static content and thus predestined to be cached
by proxies on the way to the client. A URL, serving different images, depending on a cookie's value
is not idempotent and thus is a very bad idea.

Since the sever side approach doesn't work, it is the browsers responsibility to select the
appropriate image size. An ideal adaptive image strategy should do the following:

 * Images should fit the screen, regardless of their size. An adaptive strategy needs to resize the
   image, so that it can resize into the current column width.
 * Downloading images shall minimize the required bandwidth. Large images are enjoying greater
   popularity with the advent of Retina displays, but those devices normally are connected to the
   Internet using DSL rather than mobiles, which run on 3G.
 * Not all images look good when squeezed onto a small display, particularly images with a lot of
   detail. When displaying an image on a mobile device, you might want to crop only the interesting
   part of it.

As these criteria can't be fulfilled using the well known ``<img .../>`` element,
**djangocms-cascade** offers a responsive variant, recently added to the HTML5 standard, namely the
``<picture>`` element. Using this element, the browser always fetches the image which best fits the
current layout. Additionally, if the browser runs on a high resolution (Retina) display, an image
with double resolution is downloaded. This results in much sharper images.

|edit-picture|

.. |edit-picture| image:: /_static/edit-picture.png

Picture Plugin Reference
========================

Image
-----
Clicking on the magnifying glass opens a pop-up window from django-filer_ where you can chose the
appropriate image.

.. _django-filer: https://github.com/stefanfoulis/django-filer

Image Title
-----------
This optional field shall be used to set the ``title`` tag inside the ``<picture>`` or ``<img>``
element.

Alternative Description
-----------------------
This field shall be used to set the ``alt`` tag inside the ``<picture>`` or ``<img>``
element. While the editor does require this field to be filled, it is strongly recommended to add
some basic information about that picture.

Link type
---------
Using this select box, one can chose to add an internal, or external link to the image. Please
check the appropriate section for details.

Image Shapes
------------
These checkboxes control the four CSS classes (``img-responsive``, ``img-rounded``, ``img-circle``
and ``img-thumbnail``) to be added to the ``<img ... />`` element used to render an image.

Here the option “Responsive_” has a special meaning. The problem with responsive images is, that
their size depends on the media width of the device displaying the image. Therefore we can not use
the well known ``<img ... />`` element any more. Instead, when rendering responsive images,
**djangocms-cascade** uses a ``<picture>...</picture>`` element, which is supported since Google's
Chrome 38 and can be emulated on legacy browsers using the shim picturefill.js_.

.. _Responsive: http://getbootstrap.com/css/#images-responsive
.. _picturefill.js: http://scottjehl.github.io/picturefill/

More details about this new HTML element can be found here:
https://html.spec.whatwg.org/multipage/embedded-content.html#the-picture-element

.. note:: When building web-sites with Bootstrap, I strongly recommend to always tag them as
          responsive. Otherwise they might extend over the current column width and that usually
          looks awful.

Override Picture Heights
------------------------
These settings only are available for images marked as *responsive*. They allow to crop the image
to a lower height, depending on the current media width. These heights must be specified in percent
relative to the current image height, rather than in pixels.

Absolute Image Sizes
--------------------
These settings only are available for images not marked as *responsive*. They shall be used to
resize the image to an absolute size. If either *width* or *height* is left empty, its value is
computed using the set value together with the aspect ratio of the image. If both values are set
but do not correlate with the aspect ratio of the image, then the image is cropped to fit that
size. If both *width* or *height* are left empty, the original image is used.

Resize Options
--------------
* **Upscale image**: If the original image is smaller than the desired drawing area, then the image
  is upscaled. This in general leads to blurry images and should be avoided.

* **Crop image**: If the aspect ratio of the image and the desired drawing area do not correlate,
  than the image is cropped to fit, rather than leaving white space arround it.

* **With subject location**: When cropping, use the red circle to locate the most important part of
  the image. This is a feature of Django's Filer.

* **Optimized for Retina**: Currently only available for images marked as *responsive*, this option
  adds an images variant suitable for Retina displays.

Remember shared settings
------------------------
Sometime you'd want to remember sizes and options for rendering an image across the project. In
order to not have to do this jobs for each managed image, you can remember these settings using a
name of your choice and editable in a special section of the administration backend.

Whenever you add a new picture using this plugin, a select box with these remembered settings
appears. You then can chose from one of the remembered settings, which frees you from reentering
all the values.

Moreover, by changing one of these remembered settings in the administration backend at
**Home › Cmsplugin_cascade › Shared between Plugins**, one can change the size and behavior of all
images with these settings applied to them.
