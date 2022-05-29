# Mara Superset

Automating the setup and configuration of [Apache Superset](https://github.com/apache/superset) instances from the Mara framework.

* Syncing of database
* A Makefile for running Apache Superset locally

&nbsp;

## Features

### Metadata sync

If you have a data warehouse schema defined in [Mara Schema](https://github.com/mara/mara-schema), you can automatically sync column descriptions and metric definitions with the update_metadata function in [mara_superset/metadata.py](mara_superset/metadata.py).

The database is created automatically. Datasets with their columns and metrics are synchronized after the data set table has been added manually via the UI. New columns are only added after executing the *Sync columns from Source* function via the Superset UI in the data set .

## Installation and more

Take a look at the official [Documentation](https://mara-superset.readthedocs.io/en/latest/).
