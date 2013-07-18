djangocms-style
===============

A Plugin for django CMS to add CSS classes to other plugins


Installation
------------

This plugin requires `django CMS` 2.4 or higher to be properly installed.

* In your projects `virtualenv`_, run ``pip install djangocms-style``.
* Add ``'djangocms_style'`` to your ``INSTALLED_APPS`` setting.
* Run ``manage.py migrate cmsplugin_style``.


Usage
-----

Youcan define styles in your settings.py::

CMS_STYLE_NAMES = (
    ('info', _("info")),
    ('new', _("new")),
    ('hint', _("hint")),
)
    
After that you can place other plugins inside this style plugin.
It will create a div with a class that was prior selected around this plugin.

Translations
------------

If you want to help translate the plugin please do it on transifex:

https://www.transifex.com/projects/p/django-cms/resource/djangocms-style/

