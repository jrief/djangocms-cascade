.. _bootstrap3/navbar:

======================================
Template tag for the Bootstrap3 Navbar
======================================

Although it's not derived from the ``CascadeElement`` class, this Django app is shipped with a
template tag to render the main menu inside a `Bootstrap Navbar`_. This tag is named ``main_menu``
and shall be used instead of ``show_menu``, as shipped with the DjangoCMS menu app.

.. _Bootstrap Navbar: http://getbootstrap.com/components/#navbar

Render a Navbar according to the Bootstrap3 guide:

.. code-block:: html

	{% load bootstrap3_tags %}
	...
	<div class="navbar navbar-default navbar-fixed-top" role="navigation">
	  <div class="container">
	    <div class="navbar-header">
	      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
	        <span class="sr-only">Toggle navigation</span>
	        <span class="icon-bar"></span>
	        <span class="icon-bar"></span>
	        <span class="icon-bar"></span>
	      </button>
	      <a class="navbar-brand" href="/">Project name</a>
	    </div>
	    <div class="collapse navbar-collapse">
	      <ul class="nav navbar-nav">{% main_menu %}</ul>
	    </div>
	  </div>
	</div>

Assume, the page hierarchy in DjangoCMS is set up like this:

|page-hierarchy|

.. |page-hierarchy| image:: /_static/page-hierarchy.png

then in the front-end, the navigation bar will be rendered as

|navbar|

.. |navbar| image:: /_static/navbar.png

on computer displays, and as

|navbar-mobile|

.. |navbar-mobile| image:: /_static/navbar-mobile.png

on mobile devices.

.. note:: Bootstrap3 does not support “hover”, since this event can't be handled by touch screens.
          Therefore the client has to click on the menu item, rather than moving the mouse cursor
          over it. In order to make CMS pages with children selectable, those menu items are
          duplicated. For instance, clicking on **Dropdown** in the Navbar, just opens the pull-down
          menu. Here the menu item for the page named “Dropdown” is rendered again. Clicking on this
          item, finally loads that page from the CMS.

.. note:: Bootstrap3 does not support nested menus, because they wouldn't be usable on mobile
          devices. Therefore the template tag ``main_menu`` renders only one level of children, no
          matter how deep the page hierarchy is in DjangoCMS.
