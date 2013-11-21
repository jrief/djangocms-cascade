.. _bootstrap_scaffolding:

Bootstrap Scaffolding
=====================

The two basic structure elements are the row container and the column container as described in the
`Bootstrap grid system`_. Use them to add a structure to your current placeholder.

Row container
-------------
A row container basically defines of row which spans over 12 columns. A row container can contain
from one to 12 column containers. It offers two configuration settings:

* A pull down menu, from which to select ``row`` or ``row-fluid``.
* A minimum height in CSS units (``px`` or ``em``).

Column container
----------------
A column container can be added only as direct child to a row container. It offers three
configuration settings:

* A pull down menu with the width of the column in units named ``span1`` through ``span12``.
* An optional offset from the previous column or from the rows left border named ``offset1``
  through ``offset11``.
* A minimum height in CSS units (``px`` or ``em``).

Generic HTML element: <div>
---------------------------
Use this generic HTML element, when you have to position other components inside it. It currently
offers one configuration settings:

* A minimum height in CSS units (``px`` or ``em``).

.. note:: The configuration settings for this element will probably change in the future.

Horizontal Rule element <hr>
----------------------------
Use this HTML element, to draw a horizontal line. It normally is used to separate two rows from each
other. It offers two configuration settings:

* margin-top and margin-bottom in CSS units (``px`` or ``em``).

.. _Bootstrap grid system: http://getbootstrap.com/2.3.2/scaffolding.html#gridSystem
