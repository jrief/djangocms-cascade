# Release Notes for version 1.0

Apart from dropping support for Python-2.7, **djangocms-cascade** version 1.0 internally changes a lot.
Until version 0.19 it used a special widget :class:`cmsplugin_cascade.widgets.JSONMultiWidget` which
took care of converting the so named "glossary fields" into an editor, used to change the properties
of all Cascade plugins.

While this editor was able to handle all kinds of primitive data types, such as strings, numeric input,
simple- and multiple choices, it failed to handle references onto foreign keys and other data inputs,
requiring input validation and rectification. Therefore many Cascade plugins turned into kind of hybrids,
using a mixture of classic Django form fields plus one special "glossary" field, using the ``JSONMultiWidget``
mentioned before.

This approach turned out to be impracticable, because input widgets rendered by the form fields could not
be mixed with fields rendered by the ``JSONMultiWidget``. It also was complicated from a point of understanding
and other programmers had difficulties to implement their own plugins.

Therefore in version 1.0, the list of "glossary fields" will be replaced against a slightly modified Django
``ModelForm``. This form then reads and writes its data from the Django model field
:class:`cmsplugin_cascade.models.CascadeElement.glossary`, just as it always did. This means that we still
have the advantage of using a JSON field to store arbitrary data, preventing us from having to create a Django
model for each plugin in our database.

The code for reading and writing JSON data from and to this special Django model field (ie. ``glossary``),
has been moved out of **dangocms-cascade** and into a new Django app named
[django-entangled](https://github.com/jrief/django-entangled). The reason for this code separation is greater
reusability.
