.. _installation_and_configuration:

Installation and Configuration
==============================

Install the latest stable release::

    $ pip install djangocms-bootstrap

or the current development release from github::

    $ pip install -e git+https://github.com/jrief/djangocms-bootstrap.git#egg=djangocms-bootstrap

`Download bootstrap`_ files and move the downloaded files into the folders ``static/css`` and
``static/js`` of your project's tree respectively.

Dependencies
------------

* Django_ >=1.5
* DjangoCMS_ >=3.0

Configuration
-------------

In your project's settings, add ``cmsplugin_bootstrap`` to ``INSTALLED_APPS``. Check that this entry
is located before the entry ``cms``::

  INSTALLED_APPS = (
      ...
      'cmsplugin_bootstrap',
      'cms',
      ...
  )

Update your database schema
---------------------------
run::

  ./manage.py migrate cmsplugin_bootstrap

Change your base templates
--------------------------
Add to your base template::

  <link rel="stylesheet" href="{{ STATIC_URL }}css/bootstrap.min.css" type="text/css" />

  <script src="{{ STATIC_URL }}js/bootstrap.min.js" type="text/javascript"></script>

Restrict the plugins to use
---------------------------
In case you don't want to offer all available plugins to the backend user, add this configuration
directive to your settings file. For instance::

  CMSPLUGIN_BOOTSTRAP_PLUGINS = ['container']

only loads the **Bootstraps** container plugins. If you don't define this directive, all plugins
are loaded.

.. _download bootstrap: _http://getbootstrap.com/2.3.2/getting-started.html#download-bootstrap
.. _github: https://github.com/jrief/djangocms-bootstrap
.. _Django: http://djangoproject.com/
.. _DjangoCMS: https://www.django-cms.org/
.. _pip: http://pypi.python.org/pypi/pip
