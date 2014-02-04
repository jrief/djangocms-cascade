.. _tutorial

Tutorial
========
This tutorial explains how to work with **Twitter Bootstrap**. Other CSS frameworks may behave
somehow differently.

Frontend editing
----------------
Django CMS 3.0 introduced a new frontend editing system as well as a customizable Django admin skin.

In the new system, placeholders and their plugins are no longer managed in the admin site, but
only from the frontend. Now, these plugins can be nested giving the possibility to create plugins
inside other plugins. In addition, the system offer two editing views:

* **Content View**, for editing the configuration and content of plugins.
* **Structure View**, in which plugins can be added and rearranged.

Container
---------
In **Structure View** mode, each placeholder displays a pull down menu on its right top side:
|pull-down|. When the page editor passes over this icon, a menu pulls out and offers a section of
plugins named **Bootstrap**. The kind of plugin depends on the configuration and the current plugin
type. The first plugin to add is a container:

|add-container|

The containers editing form now asks for the minimum width, its underlying grid shall use. If you
need a grid system, which maintains all columns without stacking, independently of the display size,
then choose *Tiny*. Otherwise if columns shall align on larger display but stack on smaller ones,
then choose a larger breakpoint. For details read the section `Stacked to Horizontal`_ on the
Bootstrap's documentation site.

|edit-container|

To the container itself, one can for instance add a **Bootstrap Row**.

.. |pull-down| image:: _static/edit-plugins.png
.. |add-container| image:: _static/add-container.png
.. |edit-container| image:: _static/edit-container.png
.. _Stacked to Horizontal: http://getbootstrap.com/css/#grid-example-basic

Row
---
While editing, one can specify the number of columns. If this is bigger than the current number of
columns, additional columns are added automatically. To delete columns, one must explicitly choose
the column in the context menu. Reducing the column count in the row's form editor, does not work
here.

|edit-row|

Specifying the ``min-height`` in section **Inline Styles**, will add a style attribute to the
``<div>`` element, rendering the row, using the chosen minimum height. The height must be specified
in Pixels ``px`` or ``em``'s.

.. |edit-row| image:: _static/edit-row.png

Horizontal Rule
---------------
A horizontal rule is used to separate rows optically from each other. The form editor accepts two
inline styles, to specify the top and the bottom margin for such a rule.

|rule-editor|

.. |rule-editor| image:: _static/rule-editor.png

Column
------
In the column editor, one can specify the width of each column. Since Bootstrap 3 this setting can
have more than one value, depending on the chosen display breakpoint.

|column-editor|

Since this may feel rather complicate, please refer to the corresponding Bootstrap documentation,
where the new `grid system`_ is explained detailed.

.. |column-editor| image:: _static/column-editor.png
.. _grid system: http://getbootstrap.com/css/#grid
