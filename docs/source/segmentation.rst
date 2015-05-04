.. segmentation:

=======================
Segmentation of the DOM
=======================

The **SegmentationPlugin** allows to personalize the DOM structure, depending on various parameters
supplied with the Django request object. Some use cases are:

* Depending on the user, show a different portion of the DOM, if he is a certain user or not logged
  in at all.
* Show different parts of the DOM, depending on the browsers estimated geolocation. Useful to
  render different content depending on the visitors country.
* Show different parts of the DOM, depending on the supplied marketing channel.
* Show different parts of the DOM, depending on the content in the session objects from previous
  visits of the users.
* Segment visitors into different groups used for A/B-testing.


Configuration
=============

The **SegmentationPlugin** must be activated separately on top of other **djangocms-cascade**
plugins. In ``settings.py``, add to

.. code-block:: python

	INSTALLED_APPS = (
	    ...
	    'cmsplugin_cascade',
	    'cmsplugin_cascade.segmentation',
	    ...
	)

	# this entry is optional:
	CMSPLUGIN_CASCADE_SEGMENTATION_MIXINS = (
	    'cmsplugin_cascade.segmentation.mixins.EmulateUserMixin',  # the default
	    # other segmentation plugin classes
	)


Usage
=====

When editing **djangoCMS** plugins in **Structure** mode, below the section **Generic** a new plugin
type appears, named **Segment**.

|segment-plugin|

.. |segment-plugin| image:: _static/segment-plugin.png

This plugin now behaves as an ``if`` block, which is rendered only, if the specified condition
evaluates to true. The syntax used to specify the condition, is the same as used in the Django
template language. Therefore it is possible to evaluate against more than one condition and combine
them with ``and``, ``or`` and ``not`` as described in `boolean operators`_ in the Django docs

Immediately below a segmentation block using the condition tag ``if``, it is possible to use the
tags ``elif`` or ``else``. This kind of conditional blocks is well known to Python programmers.

Note, that the context in which the condition is evaluated is the Django `request object`_.
Therefore a condition such as ``user.username == "john"``, in Django evaluates to
``request.user.username == "john"``, where ``request`` is the ``HttpRequest`` object. This means
that beside the request object, the evaluation engine does not access the remaining context.

.. _boolean operators: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#boolean-operators
.. _request object: https://docs.djangoproject.com/en/dev/ref/request-response/#httprequest-objects


Emulating Users
===============
As of version 0.5.0, in **djangocms-cascade** a staff user or administrator can emulate the
currently logged in user. If this plugin is activated, in the CMS toolbar a new menu tag appears
named “Segmentation”. Here a staff user can select another user. All evaluation conditions then
evaluate against this selected user, instead of the currently logged in user.

It is quite simple to add other overriding emulations. Have a look at the class
``cmsplugin_cascade.segmentation.mixins.EmulateUserMixin``. This class then has to be added to
your configuration settings ``CMSPLUGIN_CASCADE_SEGMENTATION_MIXINS``. It then overrides the
evaluation conditions and the toolbar menu.
