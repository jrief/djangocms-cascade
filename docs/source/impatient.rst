.. _impatient:

=================
For the Impatient
=================

This HowTo gives you a quick instruction on how to get a demo of **djangocms-cascade** up and
running. It also is a good starting point to ask questions or report bugs, since its backend is
used as a fully functional reference implementation, used by the unit tests of project.


Create a Python Virtual Environment
===================================

To keep environments separate, first create a *virtualenv*.

.. code-block:: bash

	#!/bin/sh
	sudo pip install --upgrade virtualenv
	virtualenv --distribute --no-site-packages myvirtualenv
	source myvirtualenv/bin/activate
	(myvirtualenv)$


Clone the latest stable releases
================================

Create a temporary file containing these requirements:

.. code-block:: guess

	Django==1.6.8
	Django-Select2==4.2.2
	Pillow==2.6.1
	South==1.0.1
	Unidecode==0.04.16
	argparse==1.2.1
	django-classy-tags==0.5.1
	-e git+https://github.com/divio/django-cms.git@support/3.0.x#egg=django-cms
	django-filer==0.9.8
	django-mptt==0.6.1
	django-polymorphic==0.6
	django-sekizai==0.7
	djangocms-admin-style==0.2.2
	-e git+https://github.com/jrief/djangocms-cascade.git@0.4.0#egg=djangocms-cascade
	djangocms-text-ckeditor==2.4.2
	-e git+https://github.com/jrief/easy-thumbnails.git@fix-issue-353#egg=easy-thumbnails
	html5lib==0.999
	jsonfield==1.0.0
	six==1.8.0

and install them into your environment:

.. code-block:: bash

	pip install -r requirements.txt

this will take a few minutes. After the installation finished, change into the directory containing
the demo application, install missing Stylesheets and Javascript files, initialize the database and
create a superuser:

.. code-block:: bash

	cd $VIRTUAL_ENV/src/djangocms-cascade/examples
	bower install --require
	./manage.py syncdb --migrate --settings=bs3demo.settings
	./manage runserver --settings=bs3demo.settings

Now, point a browser onto http://localhost:8000/ and log in as the super user. You now should be
able add your first page and change into **Structure** mode. To the placeholder named
``MAIN CONTENT CONTAINER`` add a plugin **Bootstrap Container**, then a **Bootstrap Row** and
finally one or more **Bootstrap Column**'s.
