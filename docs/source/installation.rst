.. _installation:

============
Installation
============

Install the latest stable release

.. code-block:: bash

	$ pip install djangocms-cascade

or the current development release from github

.. code-block:: bash

	$ pip install -e git+https://github.com/jrief/djangocms-cascade.git#egg=djangocms-cascade

Dependencies
============
* Django_ >=1.6
* DjangoCMS_ >=3.0.8


Create a database schema
========================

if you use Django-1.7 or higher

.. code-block:: bash

	./manage.py migrate cmsplugin_cascade

if you use Django-1.6

.. code-block:: bash

	./manage.py syncdb --migrate


Install Bootstrap
=================

Since the Bootstrap CSS and JavaScript files are part of their own repository, they are not shipped
within this package. Furthermore, as they are not part of the PyPI network, they have to be
installed through another package manager, namely bower_.

.. code-block:: bash

	cd djangocms-cascade
	bower install --require

Alternatively copy the installed ``bower_components`` into a directory of your project or to any
other meaningful location, but ensure that the directory ``bower_components`` can be found by
your StaticFileFinder. In doubt, add that directory to your ``STATICFILES_DIRS``:

.. code-block:: python

	STATICFILES_DIRS = (
	    os.path.abspath(os.path.join(MY_PROJECT_DIR, 'bower_components')),
	)


Configuration
=============

Add ``'cmsplugin_cascade'`` to the list of ``INSTALLED_APPS`` in the project’s ``settings.py``
file. Optionally add 'cmsplugin_cascade.extra_fields' and/or 'cmsplugin_cascade.sharable' to
the list of ``INSTALLED_APPS``. Make sure that these entries are located before the entry ``cms``.


Configure the CMS plugin
------------------------

.. code-block:: python

	INSTALLED_APPS = (
	    ...
	    'cmsplugin_cascade',
	    'cmsplugin_cascade.extra_fields',  # optional
	    'cmsplugin_cascade.sharable',  # optional
	    'cms',
	    ...
	)


Activate the plugins
--------------------

By default, no **djangocms-cascade** plugins is activated. Activate them in the project’s
``settings.py`` with the directive ``CMSPLUGIN_CASCADE_PLUGINS``.

To activate all available Bootstrap plugins, use:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.bootstrap3',)

If for some reason, only a subset of the available Bootstrap plugins shall be activated, name each
of them. If for example only the grid system shall be used, but no other Bootstrap plugins, then
configure:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.bootstrap3.container',)

A useful generic plugin is the Link-plugin. It replaces the djangocms-link_-plugin, normally used
together with the CMS.

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS += ('cmsplugin_cascade.link',)


Restrict plugins to a particular placeholder
--------------------------------------------

This setting is optional, but strongly recommended. It exclusively restricts the plugin
``BootstrapContainerPlugin`` to the placeholder ``Page Content`` (see below)

.. code-block:: python

	CMS_PLACEHOLDER_CONF = {
	    'Page Content': {
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

	CMSPLUGIN_CASCADE = {
	    ...
	    'alien_plugins': ('TextPlugin', 'FilerImagePlugin', 'OtherLeafPlugin',),
	    ...
	}


Bootstrap 3 with AngularJS
--------------------------

Some Bootstrap3 plugins can be rendered using templates which are suitable for the very popular
`Angular UI Bootstrap`_ framework. This can be done during runtime; when editing the plugin a 
select box appears which allows to chose an alternative template for rendering.


Template Customization
======================

Make sure that the style sheets are referenced correctly by the used templates. DjangoCMS requires
Django-Sekizai_ to organize these includes, so a strong recommendation is to use that Django app.

The templates used for a DjangoCMS project shall include a header, footer and the menu bar, but
should leave out an empty working area. When using HTML5, wrap this area into an ``<article>`` or
``<section>`` element. This placeholder shall be named using a meaningless identifier, for instance
"Page Content" or similar:

.. code-block:: html

	<section>{% placeholder "Page Content" %}</section>

From now on, the page layout can be adopted inside this placeholder, without having to fiddle with
template coding anymore.

.. _Django: http://djangoproject.com/
.. _DjangoCMS: https://www.django-cms.org/
.. _Angular UI Bootstrap: http://angular-ui.github.io/bootstrap/
.. _pip: http://pypi.python.org/pypi/pip
.. _Django-Sekizai: http://django-sekizai.readthedocs.org/en/latest/
.. _djangocms-link: https://github.com/divio/djangocms-link
.. _bower: http://bower.io/
