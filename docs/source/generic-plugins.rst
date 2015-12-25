.. _generic-plugins:

===============
Generic Plugins
===============


**Cascade** is shipped with a few plugins, which can be used independently of the underlying CSS
framework. To avoid duplication, they are bundled into the section **Generic** and are available
by default in the placeholders context menu.

All these plugins qualify as plugins with `extra fields`_, which means that they can be configured
by the site administrator to accept additional CSS styles and classes.


.. _extra fields: extra-fields

SimpleWrapperPlugin
===================

Use this plugin to add a wrapping element around a group of other plugins. Currently these HTML
elements can be used as wrapper: ``<div>``, ``<span>``, ``<section>``, ``<article>``. There is one
special wrapper named ``naked``. It embeds its children only logically, without actually embedding
them into any HTML element.


HorizontalRulePlugin
====================

This plugins adds a horizontal rule ``<hr>`` to the DOM.


HeadingPlugin
=============

This plugins adds a text heading ``<h1>``...``<h6>`` to the DOM. Although simple headings can be
achieved with the **TextPlugin**, there they can't be styled using special CSS classes or styles.
Here the **HeadingPlugin** can be used, since any allowed CSS class or style can be added.
