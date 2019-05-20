.. _bootstrap4/utilities:

=====================
Bootstrap 4 Utilities
=====================

Bootstrap-4 pursues the approach of offering various utilities, which can be optionally applied to
all Bootstrap elements. **djangocms-cascade** follows this approach and offers mixin classes which
can be optionally added to all Bootstrap-4 plugins. They extend their respective's plugin editor by
one or more extra fields, which the user can use to configure the appearance of the plugin.


Motivation
==========

Say, you want to configure the Bootstrap Button Plugin to use the `responsive float utilities`_.
The clumsy approach would be to add a field using a select box, for adding the float classes
``float-left``, ``float-right`` and ``float-none`` to the plugin's editor. This would be fine,
as long as these classes can only be used inside the context of a button element. The idea of
Bootstrap however is, to offer reusable components and CSS classes. Since **djangocms-cascade**
wants to follow this mindset, the editor for controlling those utilities is part of the mixin class
:class:`cmsplugin_cascade.bootstrap4.mixins.BootstrapUtilitiesMixin`.

.. _responsive float utilities: https://getbootstrap.com/docs/4.3/utilities/float/


Usage
=====

A Bootstrap-4 plugin, wanting to offer additional editable fields to the plugin's editor, should
simple add this configuration to the project's ``settings.py``:

.. code-block:: python

    CMSPLUGIN_CASCADE['plugins_with_extra_mixins'] = {
        'BootstrapButtonPlugin': BootstrapUtilities(
            BootstrapUtilities.floats,
        ),
    }


Implemented Utilitiy Properties
===============================

Currently the following utilities are implemented:

Background and Color
--------------------

This adds a combination of one CSS class for the `background and one for the foreground color`_.

.. _background and one for the foreground color: https://getbootstrap.com/docs/4.3/utilities/colors/


Margins and Paddings
--------------------

This adds all the CSS classes for `margins and paddings`_. They follow the *mobile first*
principle, which means that all selected values can be overridden by a larger media breakpoint.

.. _margins and paddings: https://getbootstrap.com/docs/4.3/utilities/spacing/


Floats
------

This adds all the CSS classes for adding `responsive float utilities`_.
