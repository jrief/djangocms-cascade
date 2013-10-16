.. _bootstrap_scaffolding:

Bootstrap Scaffolding
=====================

Django CMS 3.0 introduces a new Frontend Editing system as well as a customizable Django admin skin.

In the new system, placeholders_ and their plugins_ are no longer managed in the admin site, but
only from the frontend.

In addition, the system now offer two editing views:

* content view, for editing the configuration and content of plugins.
* structure view, in which plugins can be added and rearranged.

In structure mode each placeholder displays a pull down menu on its right side: |pull-down|. When
the users passes over this icon, a menu pulls out and offers a section of plugins named
**Bootstrap**. The two basic plugins are the row container and the column container as described in
the `Bootstrap grid system`_.

Row container
-------------
A row container basically defines of row which spans over 12 columns. A row container can contain
from one to 12 column containers. It offers a single configuration setting:

* A minimum height in CSS units (``px`` or ``em``).

Column container
----------------
A column container can be added only as direct child to a row container. It offers three
configuration settings:

* A pull down menu with the width of the column in units of 1 through 12.
* An optional offset from the previous column or from the rows left border.
* A minimum height in CSS units (``px`` or ``em``).

.. _placeholders: https://django-cms.readthedocs.org/en/latest/advanced/templatetags.html#placeholder
.. _plugins: https://django-cms.readthedocs.org/en/latest/getting_started/plugin_reference.html
.. |pull-down| image:: _static/edit-plugins.png
    :width: 48
.. _Bootstrap grid system: http://getbootstrap.com/2.3.2/scaffolding.html#gridSystem
