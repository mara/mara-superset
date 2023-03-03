Configuration
=============


Superset Configuration
----------------------

Apache Superset uses a `superset_config.py`_ file where you can configure many settings
like the superset metadata database connection, the HTTP/S port for Superset and a proxy fix.

.. _superset_config.py: https://superset.apache.org/docs/installation/configuring-superset/

Extension Configuration Values
------------------------------

The following configuration values are used by this extension. They are defined as python functions in ``mara_superset.config``
and can be changed with the `monkey patch`_ from `Mara App`_. An example can be found `here <https://github.com/mara/mara-example-project-1/blob/master/app/local_setup.py.example>`_.

.. _monkey patch: https://github.com/mara/mara-app/blob/master/mara_app/monkey_patch.py
.. _Mara App: https://github.com/mara/mara-app


.. py:data:: external_superset_url

    The URL under which the Superset instance can be reached by users e.g. https://superset.bi.example.com.

    Default: ``'http://localhost:8088'``

.. py:data:: internal_superset_url

    The URL under which the Superset instance can be reached by from mara (usually circumventing SSOs etc.).

    Default: ``'http://localhost:8088'``

.. py:data:: superset_api_username

    The email of the user for accessing the superset api. This user should be created as a superset
    user within the superset metadata database. Using a user from an authentication backend (e.g. OAuth)
    has not been tested.

    Default: ``'admin'``

.. py:data:: superset_api_password

    The password of the user for accessing the superset api

    Default: ``'admin'``

.. py:data:: superset_data_db_alias

    The alias of the database that Superset reads data from

    Default: ``'superset-data-read'``

.. py:data:: superset_data_db_name

    The name (in Superset) of the database that Superset reads from

    Default: ``'MyCompany DWH'``

.. py:data:: superset_data_db_schema

    The name of the schema where the flattered data sets for Superset are stored

    Default: ``'superset'``

.. py:data:: metadata_update_strategy

    The default update strategy to be used when synchronizing metadata

    Default: ``UpdateStrategy.CREATE | UpdateStrategy.UPDATE``
