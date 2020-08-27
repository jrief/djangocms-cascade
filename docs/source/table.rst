==============
Editing Tables
==============

Sometimes it can be useful to add some structured content to a **Django-CMS** placeholder, which
is rendered using the HTML ``<table>``-element. **DjangoCMS-Cascade** offers a special plugin to
edit such tables. This can be found in the generic section and must be activated explicitly in
your ``settings.py`` using:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = [
	    ...
	    'cmsplugin_cascade.generic.table',
	    ...
	]

This plugin depends on the third party JavaScript library `Jexcel <https://bossanova.uk/jexcel/v4/>`_
which must be installed into the Django projects using:

.. code-block:: bash

	npm install jexcel --save

.. note::
	In order to let Django find the appropriate JavaScript and CSS files for that library, you must ensure
	that ``STATICFILES_DIRS`` contains the tuple ``('node_modules', 'path/to/myproject/node_modules')``.


Usage
=====

The plugin editor only implements a subset of the functionaliy offered by the **Jexcel**-libary. Please
consolut their documentation for details. By clicking on the context menu inside the table editor one can
change the table layout and column names.


Rendering
=========

The table is rendered using the ``<table>``-element together with a table header and a table body.
