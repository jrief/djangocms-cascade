
Using DjangoCMS-Cascade
=======================
This module must be used together with DjangoCMS version 3.

DjangoCMS version 3.0
---------------------
Django CMS 3.0 introduced a new frontend editing system as well as a customizable Django admin skin.

In the new system, placeholders and their plugins_ are no longer managed in the admin site, but
only from the frontend. Now, these plugins can be nested giving the possibility to create plugins
inside other plugins. In addition, the system offer two editing views:

* **Content View**, for editing the configuration and content of plugins.
* **Structure View**, in which plugins can be added and rearranged.

In **Structure View** mode, each placeholder displays a pull down menu on its right side: |pull-down|.
When the page editor passes over this icon, a menu pulls out and offers a section of plugins named
**Bootstrap**. The kind of plugin depends on the configuration and the current plugin type.

.. note:: Not every **Bootstrap** plugin can be added as a child to another plugin.

