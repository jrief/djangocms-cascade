.. _installation_and_configuration:

Installation and Configuration
==============================

Getting the latest release
--------------------------

The easiest way to get ``djangocms-bootstrap`` is to install it using `pip`_::

    $ pip install djangocms-bootstrap

Please also check the latest source code from `github`_.

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

Update your database schema by running::

  ./manage.py migrate cmsplugin_bootstrap

.. _github: https://github.com/jrief/djangocms-bootstrap
.. _Django: http://djangoproject.com/
.. _DjangoCMS: https://www.django-cms.org/
.. _pip: http://pypi.python.org/pypi/pip
