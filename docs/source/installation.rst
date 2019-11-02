============
Installation
============

Install the latest stable release

.. code-block:: bash

	$ pip install djangocms-cascade

or the current development release from github

.. code-block:: bash

	$ pip install -e git+https://github.com/jrief/djangocms-cascade.git#egg=djangocms-cascade


Python Package Dependencies
===========================

Due to some incompatibilities in the API of Django, django-CMS and djangocms-text-ckeditor, please
only use these combinations of Python package dependencies:

djangocms-cascade-0.11.x
------------------------

* Django_ >=1.8, <=1.9
* Django-CMS_ >=3.2, <=3.3
* djangocms-text-ckeditor_ == 3.0

djangocms-cascade-0.12.x
------------------------

* Django_ >=1.9, <1.11
* Django-CMS_ >=3.4.3
* djangocms-text-ckeditor_ >= 3.3

djangocms-cascade-0.13.x
------------------------

* Django_ >=1.9, <1.11
* Django-CMS_ >=3.4.3
* djangocms-text-ckeditor_ >= 3.4

djangocms-cascade-0.14.x
------------------------

* Django_ >=1.9, <1.11
* Django-CMS_ >=3.4.4
* djangocms-text-ckeditor_ >= 3.4
* django-filer_ >= 1.2.8

djangocms-cascade-0.17.x - 0.19.x
---------------------------------

* Django_ >=1.10, <2.0
* Django-CMS_ >=3.4.4, <=3.6
* djangocms-text-ckeditor_ >= 3.4

djangocms-cascade-1.0.x
-----------------------

* Django_ >=1.11, <=2.1
* Django-CMS_ >=3.5.3, <=3.6.x
* djangocms-text-ckeditor_ >= 3.7

other combinations might work, but have not been tested.


Optional packages
-----------------

If you intend to use Image, Picture, Jumbotron, or FontIcons you will have to install django-filer
in addition:

.. code-block:: bash

	$ pip install django-filer

For a full list of working requirements see the `requirements folder`_ in the sources.

.. _requirements folder: https://github.com/jrief/djangocms-cascade/tree/master/requirements


Create a database schema
========================

.. code-block:: bash

	./manage.py migrate cmsplugin_cascade


Install Dependencies not handled by PIP
=======================================

Since the Bootstrap CSS and other JavaScript files are part of their own repositories, they are
not shipped within this package. Furthermore, as they are not part of the PyPI network, they have
to be installed through the `Node Package Manager`_, ``npm``.

In your Django projects it is good practice to keep a reference onto external node modules using
the file ``packages.json`` added to its own version control repository, rather than adding the
complete node package.

.. code-block:: bash

	cd my-project-dir
	npm init
	npm install bootstrap@3 bootstrap-sass@3 jquery@3 leaflet@1 leaflet-easybutton@2.2 picturefill select2@4 --save

If the Django project contains already a file named ``package.json``, then skip the ``npm init``
in the above command.

The node packages ``leaflet`` and ``leaflet-easybutton`` are only required if the Leaflet plugin
is activated.

The node packages ``picturefill`` is a shim to support the ``srcset`` and ``sizes`` attributes on
``<img ... />`` elements. Please check `browser support`_ if that feature is required in your
project.

The node packages ``select2`` is required for autofilling the select box in Link plugins. It is
optional, but strongly suggested.

Remember to commit the changes in ``package.json`` into the projects version control repository.

Since these Javascript and Stylesheet files are located outside of the project's ``static`` folder,
we must add them explicitly to our lookup path, using ``STATICFILES_DIRS`` in ``settings.py``:

.. code-block:: python

	STATICFILES_DIRS = [
	    ...
	    ('node_modules', os.path.join(MY_PROJECT_DIR, 'node_modules')),
	]


Using AngularJS instead of jQuery
---------------------------------

If you prefer AngularJS over jQuery, then replace the above install command with:

.. code-block:: bash

	npm install bootstrap@3 bootstrap-sass@3 angular@1.5 angular-animate@1.5 angular-sanitize@1.5 angular-ui-bootstrap@0.14 leaflet@1 leaflet-easybutton@2.2 picturefill select2@4  --save

Remember to point to the prepared AngularJS templates using this setting:

.. code-block:: python

	CMSPLUGIN_CASCADE = {
	    ...
	    'bootstrap3': {
	        'template_basedir': 'angular-ui',
	    },
	    ...
	}


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

	CMSPLUGIN_CASCADE_PLUGINS = ['cmsplugin_cascade.bootstrap3']

If for some reason, only a subset of the available Bootstrap plugins shall be activated, name each
of them. If for example, only the grid system shall be used but no other Bootstrap plugins, then
configure:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS = ['cmsplugin_cascade.bootstrap3.container']

A very useful plugin is the **LinkPlugin**. It superseds the djangocms-link_-plugin, normally used
together with the CMS.

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS.append('cmsplugin_cascade.link')

If this plugin is enabled ensure, that the node package ``select2`` has been installed and findable
by the static files finder using these directives in ``settings.py``:

.. code-block:: python

    SELECT2_CSS = 'node_modules/select2/dist/css/select2.min.css'
    SELECT2_JS = 'node_modules/select2/dist/js/select2.min.js'

:ref:`generic-plugins` which are not opinionated towards a specific CSS framework, are kept in a
separate folder. It is strongly suggested to always activate them:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS.append('cmsplugin_cascade.generic')

Sometimes it is useful to do a :ref:`segmentation`. Activate this by adding its plugin:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS.append('cmsplugin_cascade.segmentation')


When :ref:`icon-fonts`: on your site, add ``'cmsplugin_cascade.icon'`` to ``INSTALLED_APPS``
and add it to the configured Cascade plugins:

.. code-block:: python

	CMSPLUGIN_CASCADE_PLUGINS.append('cmsplugin_cascade.icon')


Special settings when using the TextPlugin
------------------------------------------

Since it is possible to add plugins from the Cascade ecosystem as children to the
`djangocms-text-ckeditor`_, we must add a special configuration:

.. code-block:: python

	from django.core.urlresolvers import reverse_lazy
	from django.utils.text import format_lazy

	CKEDITOR_SETTINGS = {
	    'language': '{{ language }}',
	    'skin': 'moono-lisa',
	    'toolbar': 'CMS',
	    'stylesSet': format_lazy('default:{}', reverse_lazy('admin:cascade_texteditor_config')),
	}

The last line in this configuration invokes a special function, which adds special configuration settings to the
CKTextEditor plugin.

.. note:: The skin ``moono-lisa`` has been introduced in Django CKEditor version 3.5, so if you upgrade from an earlier
	version, please adopt this in your settings.


Restrict plugins to a particular placeholder
--------------------------------------------

.. warning:: You **must** set ``parent_classes`` for your placeholder, else you
    won't be able to add a container to your placeholder. This means that as an
    absolute minimum, you must add this to your settings:

.. code-block:: python

	CMS_PLACEHOLDER_CONF = {
	    ...
	    'content': {
	        'parent_classes': {'BootstrapContainerPlugin': None,},
	    },
	    ...
	}

Unfortunately **django-CMS** does not allow to declare dynamically which plugins are eligible to be
added as children of other plugins. This is determined while bootstrapping the Django project and
thus remains static. We therefore must somehow trick the CMS to behave as we want.

Say, our Placeholder named "Main Content" shall accept the **BootstrapContainerPlugin** as its only
child, we then must use this CMS settings directive:

.. code-block:: python

	CMS_PLACEHOLDER_CONF = {
	    ...
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
	    ...
	}

Here we add the **BootstrapContainerPlugin** to ``plugins`` and ``parent_classes``. This is because
the Container plugin normally is the root plugin in a placeholder. If this plugin would not restrict
its parent plugin classes, we would be allowed to use it as a child of any plugin. This could
destroy the page's grid.

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
	    'alien_plugins': ['TextPlugin', 'FilerImagePlugin', 'OtherLeafPlugin'],
	    ...
	}


Bootstrap 3 with AngularJS
--------------------------

Some Bootstrap3 plugins can be rendered using templates which are suitable for the very popular
`Angular UI Bootstrap`_ framework. This can be done during runtime; when editing the plugin a
select box appears which allows to chose an alternative template for rendering.


Template Customization
======================

Make sure that the style sheets are referenced correctly by the used templates. **Django-CMS**
requires django-sekizai_ to organize these includes, so a strong recommendation is to use that
Django app.

The templates used for a **django-CMS** project shall include a header, footer, the menu bar and
optionally a breadcrumb, but should leave out an empty working area. When using HTML5, wrap this
area into an ``<article>`` or ``<section>`` element or just use it unwrapped.

This placeholder then shall be named using a generic identifier, for instance "Main Content" or
similar:

.. code-block:: html

	{% load cms_tags sekizai_tags %}
	<head>
	    ...
	    {% render_block "css" postprocessor "cmsplugin_cascade.sekizai_processors.compress" %}
	</head>

	<body>
	    ...
	    <!-- wrapping element (optional) -->
	        {% placeholder "Main Content" %}
	    <!-- /wrapping element -->
	    {% render_block "js" postprocessor "cmsplugin_cascade.sekizai_processors.compress" %}
	</body>

From now on, the page layout can be adopted inside this placeholder, without having to fiddle with
template coding anymore.

Note the two templatetags ``render_block``. The upper one collects all the CSS files referenced by
``{% addtoblock "css" ... %}``. The lower one collects all the JS files referenced by
``{% addtoblock "js" ... %}``. They then are rendered alltogether instead of beeing distributed all
across the page. If django-compressor_ is installed and enabled, then add the special compressor
``"cmsplugin_cascade.sekizai_processors.compress"`` to the templatetag. It can handle files outside
the ``STATIC_ROOT``directory.

.. _Django: http://djangoproject.com/
.. _Django-CMS: https://www.django-cms.org/
.. _Angular UI Bootstrap: http://angular-ui.github.io/bootstrap/
.. _pip: http://pypi.python.org/pypi/pip
.. _django-sekizai: http://django-sekizai.readthedocs.org/en/latest/
.. _django-compressor: http://django-compressor.readthedocs.org/en/latest/
.. _djangocms-link: https://github.com/divio/djangocms-link
.. _djangocms-text-ckeditor: https://github.com/divio/djangocms-text-ckeditor
.. _django-filer: https://github.com/divio/django-filer
.. _Node Package Manager: https://nodejs.org/en/download/
.. _browser support: https://caniuse.com/#search=srcset
