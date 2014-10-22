.. _link-plugin:

===========
Link Plugin
===========

**djangocms-cascade** ships with its own Link plugin. This is because other Cascade Plugins, such
as Button and Picture require the functionality to set links to internal- and external URLs.
However, the de-facto plugin for links, djangocms-link_ can't be used as a base class for these
plugins, therefore an alternative implementation had to be re-implemented. As all other Cascade
plugins, this implementation also keeps its data in a JSON field.

|simple-link-element|

.. |simple-link-element| image:: _static/simple-link-element.png



.. _djangocms-link: https://github.com/divio/djangocms-link
