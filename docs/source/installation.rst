.. _installation_and_configuration:

============
Installation
============

Install pandoc_ dependency on your system. It is required to convert **Markdown** into
**reStructured** text.

A strong recommendation is to

Use pip together with virtualenv
--------------------------------

.. code-block:: bash

	#!/bin/sh
	sudo pip install --upgrade virtualenv
	virtualenv --distribute --no-site-packages myvirtualenv
	source myvirtualenv/bin/activate
	(myvirtualenv)$ 

Install the latest stable release::

	$ pip install djangocms-cascade

or the current development release from github::

	$ pip install -e git+https://github.com/jrief/djangocms-cascade.git#egg=djangocms-cascade

Remember to download the CSS and Javascript files for the preferred CSS framework and place them
into the folders ``static/css`` and ``static/js`` of the project's tree. Alternatively refer them
using a Content Delivery Network.

.. note:: For simplicity, this configuration assumes, that the Bootstrap framework is used. In case
          another CSS is used, please adopt some of the proposed settings accordingly.

Dependencies
------------
* Django_ >=1.5
* DjangoCMS_ >=3.0

Update the database schema
--------------------------
run::

  ./manage.py migrate cmsplugin_cascade

this adds a single table named ``cmsplugin_cascadeelement`` to the database.

Configuration
=============
Add ``'cmsplugin_cascade'`` to the list of ``INSTALLED_APPS`` in the project’s ``settings.py``
file. Make sure that this entry is located before the entry ``cms``.

Activate the CMS plugin
-----------------------

.. code-block:: python

	INSTALLED_APPS = (
	    ...
	    'cmsplugin_cascade',
	    'cms',
	    ...
	)

Configure the CSS Framwork
--------------------------
When using the Bootstrap 3 framework

.. code-block:: python

	CMS_CASCADE_PLUGINS = ('bootstrap3',)

or, if only the grid containers from the Bootstrap 3 framework shall be used

.. code-block:: python

	CMS_CASCADE_PLUGINS = ('bootstrap3.container',)

or, if the Grid System 960 shall be used

.. code-block:: python

	CMS_CASCADE_PLUGINS = ('gs960',)

.. note:: If ``cmsplugin_cascade`` has been added to ``INSTALLED_APPS``, ``CMS_CASCADE_PLUGINS``
          *must* be set.

Restrict plugins to particular a placeholder
--------------------------------------------
This setting is optional, but strongly recommended. It exclusively restricts the plugin
``BootstrapContainerPlugin`` to the placeholder ``Page Section`` (see below)

.. code-block:: python

	CMS_PLACEHOLDER_CONF = {
	    'Page Section': {
	        'plugins': ['BootstrapContainerPlugin'],
	    },
	}

If this setting is omitted, then one can add any plugin to the named placeholder, which normally is
undesired, because it can break the page's grid.

Define the leaf plugins
-----------------------
Leaf plugins are those, which contain real data, say text or images. Hence the default setting
is to allow the **TextPlugin** and the **FilerImagePlugin** as leafs. This can be overridden using
the configuration directive

.. code-block:: python

	CMS_CASCADE_LEAF_PLUGINS = ('TextPlugin', 'FilerImagePlugin', 'OtherLeafPlugin',)

Template Customization
======================
Make sure that the style sheets are referenced correctly by the used templates. Django-CMS uses 
Django-Sekizai_ to organize these includes, so a strong recommendation is to use that tool.

The templates used for a Django-CMS project shall include a header, footer and the menu bar, but
should leave out an empty working area. When using HTML5, wrap this area into an ``<article>`` or
``<section>`` element. This placeholder can use a generic, meaningless name, say "Page Section"::

	<section>{% placeholder "Page Section" %}</section>

From now on, the page layout can be adopted inside this placeholder, without having to fiddle with
template coding anymore.

.. _github: https://github.com/jrief/djangocms-cascade
.. _Django: http://djangoproject.com/
.. _DjangoCMS: https://www.django-cms.org/
.. _Django-Sekizai: http://django-sekizai.readthedocs.org/en/latest/
.. _pip: http://pypi.python.org/pypi/pip
.. _Django-Sekizai: http://django-sekizai.readthedocs.org/en/latest/
.. _pandoc: http://johnmacfarlane.net/pandoc/
