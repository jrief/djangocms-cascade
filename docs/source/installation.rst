.. _installation_and_configuration:

Installation
============

Install the latest stable release::

	$ pip install djangocms-cascade

or the current development release from github::

	$ pip install -e git+https://github.com/jrief/djangocms-cascade.git#egg=djangocms-cascade

Remember to download the CSS and Javascript files for the preferred CSS framework and place them
into the folders ``static/css`` and ``static/js`` of the project's tree. Alternatively refer them
using a Content Delivery Network.

.. note:: For simplicity, this configuration assumes, that the Bootstrap framework is used. In case
          another CSS is used, please adopt some settings accordingly.

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
file. Make sure that this entry is located before the entry ``cms``::

	INSTALLED_APPS = (
	    ...
	    'cmsplugin_cascade',
	    'cms',
	    ...
	)

Configure the used CSS framework, for instance, when using Bootstrap 3::

	CMS_CASCADE_PLUGINS = ('bootstrap3',)

or if only the grid containers from the Bootstrap 3 framework shall be used::

	CMS_CASCADE_PLUGINS = ('bootstrap3.container',)

or if the Grid System 960 shall be used::

	CMS_CASCADE_PLUGINS = ('gs960',)

This setting is optional, but strongly recommended. It exclusively restricts the plugin
``BootstrapContainerPlugin`` to the placeholder ``Page Section`` (see below)::

	CMS_PLACEHOLDER_CONF = {
	    'Page Section': {
	        'plugins': ['BootstrapContainerPlugin'],
	    },
	}

If this setting is omitted, then one can add any plugin to the named placeholder, which normally is
undesired, because it can break the page's grid.

Adopt the templates
-------------------
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
