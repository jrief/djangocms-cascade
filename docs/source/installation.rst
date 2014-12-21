.. _installation:

============
Installation
============

A strong recommendation is to use

pip with virtualenv
-------------------

.. code-block:: bash

	#!/bin/sh
	sudo pip install --upgrade virtualenv
	virtualenv --distribute --no-site-packages myvirtualenv
	source myvirtualenv/bin/activate
	(myvirtualenv)$ 

Install the latest stable release

.. code-block:: bash

	$ pip install djangocms-cascade

or the current development release from github

.. code-block:: bash

	$ pip install -e git+https://github.com/jrief/djangocms-cascade.git#egg=djangocms-cascade

Remember to download the CSS and Javascript files for the preferred CSS framework and place them
into the folders ``static/css`` and ``static/js`` of the project's tree. Alternatively refer them,
using a Content Delivery Network.

.. note:: For simplicity, this configuration assumes, that the Bootstrap framework is used. In case
          another CSS shall be used, adopt the proposed settings accordingly.

With bower_ install the Bootstrap CSS and JavaScript files into the root directory of your project
or to any other meaningful location. Ensure that the directory ``bower_components`` can be found by
your StaticFileFinder. In doubt, add that directory to your ``STATICFILES_DIRS``.

Dependencies
------------
* Django_ >=1.6
* DjangoCMS_ >=3.0.8

Known working environment
-------------------------

As for 2014-12-20, this is a known working environment. In the future (hopefully) all required
Python packages will be available through PyPI.

.. code-block:: guess

	Django==1.6.8
	Django-Select2==4.2.2
	MarkupSafe==0.23
	Pillow==2.6.1
	South==1.0.1
	Sphinx==1.2.2
	Unidecode==0.04.16
	argparse==1.2.1
	django-classy-tags==0.5.1
	-e git+https://github.com/divio/django-cms.git@c9a27abc420893b2d8e4a3496536841d4cdccee8#egg=django_cms
	django-filer==0.9.8
	django-mptt==0.6.1
	django-polymorphic==0.6
	django-sekizai==0.7
	djangocms-admin-style==0.2.2
	djangocms-text-ckeditor==2.3.0
	docutils==0.12
	-e git+https://github.com/jrief/easy-thumbnails.git@de5213f92d7e5ea7bfefc24b02ba14809e4af567#egg=easy_thumbnails
	html5lib==0.999
	jsonfield==1.0.0
	six==1.8.0
	wsgiref==0.1.2


Update the database schema
--------------------------

.. code-block:: bash

	./manage.py migrate cmsplugin_cascade

Install Bootstrap
-----------------

Since the Bootstrap files are part of their own repository, I dislike the idea of copying them into
this repository. Instead you should install them using bower.

.. code-block:: bash

	cd djangocms-cascade
	bower install bootstrap


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

	CMSPLUGIN_CASCADE_LEAF_PLUGINS = ('TextPlugin', 'FilerImagePlugin', 'OtherLeafPlugin',)


Bootstrap 3 with AngularJS
--------------------------

To replace Bootstrap's jQuery code against the very popular `Angular UI Bootstrap`_, add 

.. code-block:: python

	CMSPLUGIN_CASCADE_BOOTSTRAP3_TEMPLATE_DIR = 'cascade/angular-ui'

to your ``settings.py``. This will load the rendering templates created for AngularJS from a
different directory.

Configure the 960.gs Framework
==============================

Currently the 960.gs framework has no meaningful user settings.


Template Customization
======================

Make sure that the style sheets are referenced correctly by the used templates. DjangoCMS requires
Django-Sekizai_ to organize these includes, so a strong recommendation is to use that tool.

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
