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
* Django_ >=1.8
* DjangoCMS_ >=3.2


Create a database schema
========================

.. code-block:: bash

	./manage.py migrate cmsplugin_cascade


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
	    'cmsplugin_cascade.clipboard',  # optional
	    'cmsplugin_cascade.extra_fields',  # optional
	    'cmsplugin_cascade.sharable',  # optional
	    'cmsplugin_cascade.segmentation',  # optional
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

A very useful plugin is the **LinkPlugin**. It superseds the djangocms-link_-plugin, normally used
together with the CMS.

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS += ('cmsplugin_cascade.link',)

:ref:`generic-plugins` which are not opinionated towards a specific CSS framework, are kept in a
separate folder. It is strongly suggested to always activate them:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.generic',)


Sometimes it is useful to do a :ref:`segmentation`. Activate this by adding its plugin:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = ('cmsplugin_cascade.segmentation',)


Restrict plugins to a particular placeholder
--------------------------------------------

.. warning:: You **must** set ``parent_classes`` for your placeholder, else you
    won't be able to add a container to your placeholder. This means that as an
    absolute minimum, you must add this to your settings:

    .. code-block:: python

        CMS_PLACEHOLDER_CONF = {
            'content': {
                'parent_classes': {'BootstrapContainerPlugin': None,},
            },
        }


Unfortunately **djangoCMS** does not allow to declare dynamically which plugins are eligible to be
added as children of other plugins. This is determined while bootstrapping the Django project and
thus remain static. We therefore must somehow trick the CMS to behave as we want.

Say, our Placeholder named "Main Content" shall accept the **BootstrapContainerPlugin** as its only
child, we then must use this CMS settings directive:

.. code-block:: python

	CMS_PLACEHOLDER_CONF = {
	    'Main Content Placeholder': {
	        'plugins': ['BootstrapContainerPlugin'],
	        'text_only_plugins': ['TextLinkPlugin'],
	        'parent_classes': {'BootstrapContainerPlugin': None},
	        'glossary': {
	            'breakpoints': ['xs', 'sm', 'md', 'lg'],
	            'container_max_widths': {'xs': 750, 'sm': 750, 'md': 970, 'lg': 1170},
	            'fluid': False,
	            'media_queries': {
	                'xs': ['(max-width: 768px)'],
	                'sm': ['(min-width: 768px)', '(max-width: 992px)'],
	                'md': ['(min-width: 992px)', '(max-width: 1200px)'],
	                'lg': ['(min-width: 1200px)'],
	            },
	        },
	    },
	}

Here we add the **BootstrapContainerPlugin** to ``plugins`` and ``parent_classes``. This is because
the Container plugin normally is the root plugin in a placeholder. If this plugin would not restrict
its parent plugin classes, we would be allowed to use it as a child of any plugin. This could
destroy the page's grid.

.. note:: Until version 0.7.1 the Container plugin did not restrict it's ``parent_classes`` and
		therefore we did not have to add it to the ``CMS_PLACEHOLDER_CONF`` settings.

Furthermore, in the above example we must add the **TextLinkPlugin** to ``text_only_plugins``.
This is because the **TextPlugin** is not part of the Cascade ecosystem and hence does not know
which plugins are allowed as its children.

The dictionary named ``glossary`` sets the initial parameters of the :ref:`bootstrap3/grid`.


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

The templates used for a DjangoCMS project shall include a header, footer, the menu bar and
optionally a breadcrumb, but should leave out an empty working area. When using HTML5, wrap this
area into an ``<article>`` or ``<section>`` element or just use it unwrapped (suggested). This
placeholder shall be named using a generic identifier, for instance "Main Content" or similar:

.. code-block:: html

	{% load cms_tags %}

	<!-- wrapping element (optional) -->
	    {% placeholder "Main Content" %}
	<!-- /wrapping element -->

From now on, the page layout can be adopted inside this placeholder, without having to fiddle with
template coding anymore.

.. _Django: http://djangoproject.com/
.. _DjangoCMS: https://www.django-cms.org/
.. _Angular UI Bootstrap: http://angular-ui.github.io/bootstrap/
.. _pip: http://pypi.python.org/pypi/pip
.. _Django-Sekizai: http://django-sekizai.readthedocs.org/en/latest/
.. _djangocms-link: https://github.com/divio/djangocms-link
.. _bower: http://bower.io/
