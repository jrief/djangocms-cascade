.. _bs3-grid:

=======================
Bootstrap 3 Grid system
=======================
In order to make full take full advantage of **djangocms-cascade**, you should be familiar with the
concepts of the `Bootstrap Grid System`_, since all other Bootstrap components depend upon.

.. _Bootstrap Grid System: http://getbootstrap.com/css/#grid

Container
=========
A **Container** is the outermost component the Bootstrap framework knows of. Here the designer can
specify the breakpoints of a Web site. By default, Bootstrap offers 4 breakpoints: “large”,
“medium”, “small” and “tiny”. These determine for which kind of screen widths the grid system may
switch the layout.

The editor window for a Container element offers three options which affect all its child plugins.

|edit-container|

.. |edit-container| image:: /_static/edit-container.png

Small devices exclusively
-------------------------
If the Web site shall be optimized just for small but not for large devices, then set the
**Widest Display** to *Medium*, *Small* or *Tiny*. In the project's style sheets, the maximum width
of the container element, then must be reduced to that chosen breakpoint:

.. code-block:: css

	@media(min-width: 1200px) {
	  .container {
	    max-width: 970px;
	  }
	}

or, if you prefers the SASS syntax:

.. code-block:: css

	@media(min-width: $screen-lg) {
	  .container {
	    max-width: $container-desktop;
	  }
	}

Large devices exclusively
-------------------------
If the Web site shall be optimized just for large but not for small devices, then set the
**Narrowest Display** to *Small*, *Medium* or *Large*. Here no adoption to the style sheets are
required.

Fluid Container
---------------
A variant of the normal Bootstrap Container is the Fluid Container. It can be enabled by a checkbox
in the editors window. Fluid Containers have no hards breakpoints, they adopt their width to
whatever the browser pretends.

A fluid container makes it impossible to determine the maximum width of responsive images in
advance. Hence, if responsive images shall be used, its use is discouraged. Please also see the note
below.

Row
===
Each Bootstrap Container may contain one or more Bootstrap Rows. A row does not accept any
configuration setting. However, while editing, one can specify the number of columns. If adding a
row, then this number of columns are added. If editing a row, then columns only are added, if this
value exceeds the current number of columns. Reducing the number of columns does not delete any of
them; they must explicitly be chosen from the context menu in structure view.

|edit-row|

Specifying the ``min-height`` in section **Inline Styles**, will add a style attribute to the
``<div>`` element, rendering the row, using the chosen minimum height. The height must be specified
in Pixels ``px`` or ``em``'s.

.. |edit-row| image:: /_static/edit-row.png

Horizontal Rule
===============
A horizontal rule is used to separate rows optically from each other. The form editor accepts two
inline styles, to specify the top and the bottom margin for such a rule.

|rule-editor|

.. |rule-editor| image:: /_static/rule-editor.png

Column
======
In the column editor, one can specify the width, the offset and the visibility of each column.
These values can be set for each of the four breakpoints (*tiny*, *small*, *medium* and *large*),
as specified by the Container Plugin.

At the beginning this may feel rather complicate, but remember that **Bootstrap 3 is mobile first**,
therefore all column settings, *first* are applied to the narrow breakpoints but can be overridden
for larger breakpoints at a later stage. This is the reason why the editor starts with the column
widths and offsets for tiny rather than large displays.

|edit-column|

.. |edit-column| image:: /_static/edit-column.png

.. note:: If the current column is member of a container which differs from the default breakpoint
          settings (*large* for the widest, and *tiny* for the smallest display), then that column
          editor shows up only with the input fields for the enabled breakpoints.

Adding Plugins into a hard coded grid
=====================================
Sometimes the given Django template already defines a Bootstrap container, or even a row inside a
container component. Example:

.. code-block:: html

	<div class="container">
	    {% placeholder "Row Content" %}
	</div>

Here the Django templatetag ``{% placeholder "Row Content" %}`` requires a Row- rather than a
Container-plugin. Now we must tell **djangocms-cascade** which breakpoints shall be allowed and what
the containers extensions shall be. This must be hard-coded using the following setting:

.. code-block:: python

	CMS_PLACEHOLDER_CONF = {
	    # other placeholder configurations ...
	    'Row Content': {
	        'plugins': ['BootstrapRowPlugin'],
	        'parent_classes': {'BootstrapRowPlugin': []},
	        'require_parent': False,
	        'glossary': {
	            'breakpoints': ['xs', 'sm', 'md', 'lg'],
	            'container_max_widths': {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170},
	        }
	    }
	}

Please refer to the `DjangoCMS documentation`_ for details about these settings with the exception
of ``glossary``. This setting is special to **djangocms-cascade**, it is a dictionary which gives
the placeholder the ability to behave like a plugin for the Cascade app. Remember, each Cascade
plugin stores all of its settings inside a Python dictionary which is serialized into a single
database field. By having a placeholder behaving like a plugin, this dictionary must be emulated
using the settings variable ``CMS_PLACEHOLDER_CONF``.

.. _DjangoCMS documentation: https://django-cms.readthedocs.org/en/latest/basic_reference/configuration.html#std:setting-CMS_PLACEHOLDER_CONF

Nested Columns and Rows
=======================
One of the great features of Bootstrap is the ability to nest Rows inside Columns. These nested Rows
then can contain Columns of 2nd level order. A quick example:

.. code-block:: html

	<div class="container">
	  <div class="row">
	    <div class="col-md-3">
	      Left column
	    </div>
	    <div class="col-md-9">
	      <div class="row">
	        <div class="col-md-6">
	          Left nested column
	        </div>
	        <div class="col-md-6">
	          Right nested column
	        </div>
	      </div>
	    </div>
	  </div>
	</div>

rendered, it would look like:

|nested-rows|

.. |nested-rows| image:: /_static/nested-rows.png

If a responsive image shall be placed inside a column, we must estimate the width of this image, so
that when rendered, it fits exactly into that column. We want easy-thumbnails_ to resize our images
to the columns width and not having the browser to up- or down-scale them.

.. _easy-thumbnails: https://github.com/SmileyChris/easy-thumbnails

Therefore **djangocms-cascade** keeps track of all the breakpoints and the chosen column widths.
For simplicity, this example only uses the breakpoint “medium”. The default Boostrap settings for
this width is 992 pixels. Doing simple math, the outer left column widths gives
3 / 12 * 992 = 248 pixels. Hence, adding a responsive image to that column means, that
**easy-thumnails** automatically resizes it to a width of 248 pixels.

To calculate the width of the nested columns, first evaluate the width of the outer right column,
which is 9 / 12 * 992 = 744 pixels. Then this width is subdivided again, using the the width of the
nested columns, which is 6 / 12 * 744 = 372 pixels.

These calculations are always performed recursively for all nested column and for all available
breakpoints.

.. warning:: As the name implies, a container marked as *fluid*, does not specify a fixed width.
             Hence it is impossible to calculate the width of an image marked as responsive inside
             such a container. Therefore, its use is discouraged.
