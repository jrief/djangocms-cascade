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
by proxies on the way to the client. A URL, serving different images, thus is a very bad idea.

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

Link type
---------
Chose whether a Link shall open in the current or a new window.

Shared settings
---------------
If a plugin 