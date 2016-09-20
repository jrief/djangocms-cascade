.. _impatient:

=================
For the Impatient
=================

This HowTo gives you a quick instruction on how to get a demo of **djangocms-cascade** up and
running. It also is a good starting point to ask questions or report bugs, since its backend is
used as a fully functional reference implementation, used by the unit tests of project.


Create a Python Virtual Environment
===================================

To keep environments separate, create a virtual environment and install external dependencies.
Missing packages with JavaScript files and Style Sheets, which are not available via pip must be
installed via npm:

.. code-block:: bash


    $ git clone https://github.com/jrief/djangocms-cascade.git
	$ cd djangocms-cascade
	$ virtualenv cascadenv
	$ source cascadenv/bin/activate
	(cascadenv)$ pip install -r requirements/django19.txt
	(cascadenv)$ npm install


Initialize the database, create a superuser and start the development server:

.. code-block:: bash

	cd examples
	./manage.py migrate
	./manage.py createsuperuser
	./manage.py runserver

Point a browser onto http://localhost:8000/ and log in as the super user. Here you should be able
to add your first page. Do this by changing into into **Structure** mode on the top of the page.
Now a heading named **Main Content** appears. This heading symbolizes our main **djangoCMS**
Placeholder.

Locate the plus sign right to the heading and click on it. From its context menu select
**Container** located in the section **Bootstrap**:

|add-container|

.. |add-container| image:: _static/add-container.png

This brings you into the editor mode for a Bootstrap container. To this container you may add one or
more Bootstrap **Rows**. Inside these rows you may organize the layout using some Bootstrap
**Columns**.

Please proceed with the detailled explanation on how to use the
:ref:`Bootstrap's grid <bootstrap3/grid>` system within **djangocms-cascade**.
