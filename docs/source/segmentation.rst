.. segmentation:

=======================
Segmentation of the DOM
=======================

The **SegmentationPlugin** allows to personalize the DOM structure, depending on various parameters
supplied with the Django request object. Some use cases are:

* Depending on the user, show a different portion of the DOM, if he is logged in or anonymous.
* Show different parts of the DOM, depending on the browsers estimated geolocation.
* Show different parts of the DOM, depending on the supplied marketing channel.
* Show different parts of the DOM, depending on the content in the session objects from previous
  visits of the users.


Configuration
=============

The **SegmentationPlugin** must be activated separately on top of other **djangocms-cascade**
plugins. In ``settings.py``, add to

.. code-block: python

	INSTALLED_APPS = (
	    ...
	    'cmsplugin_cascade',
	    'cmsplugin_cascade.segmentation',
	    ...
	)


Usage
=====

