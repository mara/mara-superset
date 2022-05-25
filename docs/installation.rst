Installation
============

Python Version
--------------

We recommend using the latest version of Python. Mara supports Python
3.6 and newer.

Dependencies
------------

These packages will be installed automatically when installing Mara Superset.

* `Mara DB`_ implements database integration withing the Mara Framework.
* `Mara Page`_ the basics for UI pages based on Flask.
* `Mara Schema`_ modelling of data models within the Mara Framework.
* `Click`_ is a framework for writing command line applications. It provides
  the ``flask`` command and allows adding custom management commands.
* `Requests`_ is a simple HTTP library used to interact with the Superset API.

.. _Mara DB: https://github.com/mara/mara-db
.. _Mara Page: https://github.com/mara/mara-page
.. _Mara Schema: https://github.com/mara/mara-schema
.. _Click: https://palletsprojects.com/p/click/
.. _Requests: https://requests.readthedocs.io/en/latest/

Install Mara Superset
---------------------

There are two options to install:

* **Option 1:** Install with local superset instance
* **Option 2:** Using an already existing superset database

For option 1 follow the step-by-step guide until the end. For option 2 follow the guide and skip the steps 3 to 6.

#. Add the ``mara-superset`` package to your mara project

#. Add ``.scripts/mara-superset/superset.mk`` to your Makefile

#. Call ``make install-local-superset``

#. In case you want to connect to a Microsoft SQL database, call `make install-local-superset-mssql` as well

#. Create a new postgres database via sql statement ::

    CREATE DATABASE superset_metadata ENCODING UTF8 TEMPLATE template0;

#. Create a `supserset config file <https://superset.apache.org/docs/installation/configuring-superset>`_ at `app/superset_config.py` with the following content: ::

    # Superset specific config
    ROW_LIMIT = 5000

    SUPERSET_WEBSERVER_PORT = 8088

    # Flask App Builder configuration
    # Your App secret key
    SECRET_KEY = 'USE_YOUR_OWN_SECURE_RANDOM_KEY'

    # The SQLAlchemy connection string to your database backend
    # This connection defines the path to the database that stores your
    # superset metadata (slices, connections, tables, dashboards, ...).
    # Note that the connection information to connect to the datasources
    # you want to explore are managed directly in the web UI
    SQLALCHEMY_DATABASE_URI = 'postgresql:///superset_metadata'

    # Flask-WTF flag for CSRF
    WTF_CSRF_ENABLED = True
    # Add endpoints that need to be exempt from CSRF protection
    WTF_CSRF_EXEMPT_LIST = []
    # A CSRF token that expires in 1 year
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

    # Set this API key to enable Mapbox visualizations
    MAPBOX_API_KEY = ''

#. Call `make install-superset` to initialize the superset database and then call `make run-superset` which will start Apache Superset in a gunicorn app in console.

   Now you should be able to log in to superset via http://localhost:8088

   The default username is `admin` and the password `admin` as well.

#. Patch the `app/local_setup.py` file with the following content: ::

    import mara_superset.config

    # the external URL for your superset instance
    patch(mara_superset.config.external_superset_url)(lambda: 'https://external-superset-url.com/')

    # the internal URL used for API calls
    patch(mara_superset.config.internal_superset_url)(lambda: 'https://internal-superset-dns-name.local/')

    # the api username and password
    patch(mara_superset.config.superset_api_username)(lambda: 'admin')
    patch(mara_superset.config.superset_api_password)(lambda: 'admin')

    # the mara db alias for the database containing superset datasets
    patch(mara_superset.config.superset_data_db_alias)(lambda: 'superset-data-read')

    # the name of the database in Superset
    patch(mara_superset.config.superset_data_db_name)(lambda: 'MyCompany DWH')

    # the schema to be used for superset data sets
    patch(mara_superset.config.superset_data_db_schema)(lambda: 'superset')
