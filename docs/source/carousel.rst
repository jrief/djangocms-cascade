.. _bootstrap_carousel:

Bootstrap Carousel
==================

A `Bootstrap Carousel`_ can be added to DjangoCMS without having to install another CMS plugin. It
uses the exiting database tables, which are already available for the other Bootstrap CMS plugins.

To add a Carousel use the common frontend editor.
* From the section **Bootstrap**, add a plugin of type **Carousel**.
* Next add as many plugins of type **Slide** to this **Carousel** plugin.
* Add plugins of any kind to this **Slide** plugin. Normally, this will be an **ImagePlugin**, but
you may also add a **TextPlugin** or a **VideoPlugin** or anything you like.

Installation
------------
The Bootstrap Carousel requires JavaScript to function properly. Therefore make sure that these two
lines are included somewhere in your templates::

	<script src="//code.jquery.com/jquery-1.10.2.min.js" type="text/javascript"></script>
	<script src="//netdna.bootstrapcdn.com/bootstrap/2.3.2/js/bootstrap.min.js" type="text/javascript"></script>

.. note:: I personally prefer to run Bootstrap with AngularJS_ instead of *jQuery*. Fortunately most
          UI elements from Bootstrap, which by default require *jQuery*, now are available through
          the `Angular UI Bootstrap`_ library. I therefore rewrote the Carousel and Slide templates
          and made them available through the template library djangocms-angular-compendium_ which
          shall be installed side by side with this **djangocms-bootstrap** library.

Styling
-------
A **Carousel** offers the usual CSS styles ``margin-top``, ``margin-right``, ``margin-bottom`` and
``margin-left``. Additionally it offers two input settings for ``width`` and a ``height``. These
dimensions are used to crop the child slides. This might be required, so that slides of different
size can be added to the Carousel without having the screen to jump up and down during a slide
change.

For a **Slide**, currently no styling options are available.

Options
-------
The Bootstrap Carousel's behavior can be configured with two option. This is ``interval`` and
``pause``. Please read the Bootstrap documentation about how to use these options.

Slide Captions
--------------
This plugin uses the *caption* and *description* text, as editable inside the **ImagePlugin**.

For Carousel slides, Bootstrap offers a special CSS class named ``carousel-caption``. This displays
caption and description text in a dark box at the bottom of the image. Since this differs from, how
the ImagePlugin renders caption text, overload the image rendering template.

Copy the image rendering template to the same relative path location in the project's ``templates``
directory. Then add the following template code snippet to that template::
	
	{# image rendering code #}
	{% if bootstrap_element == "carousel" %}
	  {% if instance.caption or instance.description %}<div class="carousel-caption">{% endif %}
	  {% if instance.caption %}<h4>{{ instance.caption }}</h4>{% endif %}
	  {% if instance.description %}<p>{{ instance.description }}</p>{% endif %}
	  {% if instance.caption or instance.description %}</div>{% endif %}
	{% else %}
	  {# other caption rendering code #}
	{% endif %}

.. _Bootstrap Carousel: http://getbootstrap.com/2.3.2/javascript.html#carousel
.. _AngularJS: http://angularjs.org/
.. _Angular UI Bootstrap: http://angular-ui.github.io/bootstrap/#/carousel
.. _djangocms-angular-compendium: https://github.com/jrief/djangocms-angular-compendium
