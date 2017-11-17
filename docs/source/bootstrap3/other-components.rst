=============
Panel element
=============

Bootstrap is shipped with CSS helpers to facilitate the creation of Panels_. In **djangocms-cascade**
these panels can be added to any placholder. In the context menu of a placeholder, select **Panel**
below the section **Bootstrap** and chose the style. The panel heading and footer are optional.
As body, the panel element accepts other plugins, normally this is a Text plugin.

.. _Panels: http://getbootstrap.com/components/#panels

.. bootstrap3/jumbotron

=========
Jumbotron
=========

Bootstrap is shipped with CSS helpers to facilitate the creation of a Jumbotron_, sometimes also
named "Hero" element. In **djangocms-cascade**, such a Jumbotron plugin can be added anywhere,
even as the root element of a placeholder, in other words, even outside of a Bootstrap Container
plugin. The latter configuration is specially useful for images, which shall extend over the full
width of the web page.

If used outside a Bootstrap Container, we first must configure the allowed breakpoints. This is
the same behaviour as for the Container plugin. Then we optionally can chose an image or a
background color, it's size, attachment, position and repetitions. For more details read
`this article`_ on how to configure background images using pure CSS.

A Jumbotron without any content has a default height of 96 pixels, which is 48 pixels for the
top- and bottom paddings, each. These values are given by the Bootstrap 3 framework.

To increase the height of a Jumbotron you have two choices. The simpler one is to add some
content to the Jumbotron plugin which then increases it's height. Another, is to explicitly
to set other padding of the Jumbotron plugin.

.. _Jumbotron: http://getbootstrap.com/components/#jumbotron
.. _this article: https://css-tricks.com/almanac/properties/b/background-image/


========
Tab Sets
========

Bootstrap is shipped with CSS helpers to facilitate the creation of Tabs_. In **djangocms-cascade**,
such a Tab plugin can be added anywhere inside columns or rows.

In the context menu of a placeholder, select **Tab Set**. Depending on the chosen number of
children, it will add as many **Tab Pane**s. Each **Tab Pane** has a Title field, its content is
displayed in the tab. Below a **Tab Pane** you are free to add whatever you want.


.. _Tabs: http://getbootstrap.com/javascript/#tabs

==============
Secondary menu
==============

.. warning:: This plugin is experimental. It may disappear or be replaced. Use it at your own risk!

Often there is a need to add secondary menus at arbitrary locations. The **Secondary menu** plugin
can be used in any placeholder to display links onto child pages of a CMS page. Currently only
pages marked as **Soft Root** with a defined **Page Id** are allowed as parent of such a secondary
menu.

.. note:: This plugins reqires the template tag ``main_menu_below_id`` which is shipped with
          djangocms-bootstrap3_

.. _djangocms-bootstrap3: https://github.com/jrief/djangocms-bootstrap3
