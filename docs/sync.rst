Synchronization
===============

The extension supports synchronizing the data models as metadata to `Apache Superset`_.

.. _Apache Superset: https://superset.apache.org

Defining the update strategy
----------------------------

The update strategy is defined via an flag Enum ``UpdateStrategy`` which supports the following options:


.. py:data:: CREATE

    When the model does not exist in Superset, create it

.. py:data:: UPDATE

    When the model exists already in Superset, update its columns. Columns which where removed will be retained and return a 'NULL' value.

    .. warning::
        New columns are (currently) not added automatically. You need to run schema sync. manually in Superset and then run the metadata sync again.
        This might drop columns which does not exist anymore leaving existing charts in an inconsistent state (!).

.. py:data:: REPLACE

    When the model exists already in Superset, delete and recreate it.

.. py:data:: DELETE

    when a data model exists in Superset but not in the Mara Schema definition, delete it.
    SQL Views created in Apache Superset SQL Lab are not deleted.


By default the update strategy `CREATE | UPDATE` is used. You can define the update strategy
via the configuration (``metadata_update_strategy``) or by passing the parameter
`update_strategy` to the function `mara_superset.metadata.update_metadata`.


We suggest using the `CREATE | UPDATE` strategy for production environments and `CREATE | REPLACE | DELETE` for development and test environments.


Execute Metadata sync.
----------------------



.. tabs::

    .. group-tab:: CLI

        .. code-block:: text

            $ flask mara_superset.update-metadata

    .. group-tab:: Mara Pipeline

        .. code-block:: python

            from mara_pipelines.commands.python import RunFunction
            from mara_pipelines.pipelines import Pipeline, Task

            pipeline = Pipeline(
                id="update_frontends",
                description="Updates various frontends")

            import mara_superset.metadata

            update_pipeline.add(
                Task(id='update_superset_metadata',
                    description='Flushes all field value caches in Superset and updates metadata',
                    commands=[RunFunction(mara_superset.metadata.update_metadata)]))

    .. group-tab:: Python

        .. code-block:: python

            from mara_superset.metadata import UpdateStrategy, update_metadata

            # running only with update stragy UPDATE not creating any missing models
            update_metadata(update_strateg=UpdateStrategy.UPDATE)
