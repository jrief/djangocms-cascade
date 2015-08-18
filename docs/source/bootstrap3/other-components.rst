.. _bootstrap3/other-components:

=============
Panel element
=============

Bootstrap is shipped with CSS helpers to facilitate the creation of Panels_. In **djangocms-cascade**
these panels can be added to any placholder. In the context menu of a placeholder, select **Panel**
below the section **Bootstrap** and chose the style. The panel heading and footer are optional.
As body, the panel element accepts other plugins, normally this is a Text plugin.

.. _Panels: http://getbootstrap.com/components/#panels


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
