API
===

.. module:: mara_superset

This part of the documentation covers all the interfaces of Mara Superset.  For
parts where the package depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Metadata Synchronization
------------------------

.. module:: mara_superset.metadata

.. autofunction:: update_metadata

.. autofunction:: superset_description

.. autofunction:: superset_metric_expression

.. autofunction:: superset_metric_d3format


Superset API Client
-------------------

.. module:: mara_superset.client

.. autoclass:: SupersetClient
   :members:
   :inherited-members:
