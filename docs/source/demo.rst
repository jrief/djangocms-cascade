.. demo

============
Run the demo
============

Prepare the environment
-----------------------
Assuming that you run Python in a `virtual environment`_ , make sure these packages are installed.

.. _virtual environment: http://www.virtualenv.org/en/latest/

.. code-block:: bash

	pip install -r requirements.txt

Prefill the database
--------------------
Change into the directory ``examples`` and populate the database

.. code-block:: bash

	./manage.py syncdb --migrate

Answer the questions about the admin user, then start the Django development server

.. code-block:: bash

	./manage.py runserver --settings=bootstrap3.settings

or, if you prefer to play with 960.gs

.. code-block:: bash

Run the demo server
-------------------

.. code-block:: bash

	./manage.py runserver --settings=gs960.settings

As usual, this command shall only be used for development.

Browse the demo site
--------------------
Point a browser onto http://localhost:8000/ and add a page to the CMS using the template
**Default Page**. This template contains a header with a menu bar, a footer and a single
DjangoCMS placeholder, named **Page Content**.

Start to populate this placeholder with some plugins as found in the context menu on the right hand
side. 

**960.gs** allows to add a **Container 12** or a **Container 16**, followed by a **Grid** plugin.
For details, please have a look at the :ref:`tutorial-gs960`.

Bootstrap allows to add a **Container**, followed by a **Row**, followed by a **Column** plugin.
For details, please have a look at the :ref:`tutorial-bs3`.

Finally add one of the leafs, such as the well known **Text** or **Image** plugins.
