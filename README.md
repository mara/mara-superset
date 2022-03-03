# Mara Superset

Automating the setup and configuration of [Apache Superset](https://github.com/apache/superset) instances from the Mara framework.

* Syncing of database
* A Makefile for running Apache Superset locally

&nbsp;

## Installation

### Option 1: Install with local superset instance

Follow the steps until the end.

### Option 2: Using an already existing superset database

Skip the steps 3 to 6.

&nbsp;

1. Add the `mara-superset` package to your mara project
2. Add `.scripts/mara-superset/superset.mk` to your Makefile

3. Call `make install-local-superset`
4. In case you want to connect to a Microsoft SQL database, call `make local-superset-mssql` as well
5. Create a new postgres database via sql statement
```sql
CREATE DATABASE superset_metadata ENCODING UTF8 TEMPLATE template0;
```
5. Create a [supserset config](https://superset.apache.org/docs/installation/configuring-superset) at `app/superset_config.py` with the following content:
``` py
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
```
6. Call `make install-superset` to initialize the superset database

Now you should be able to log in to superset via http://localhost:8088

7. Patch the `app/local_setup.py` file with the following content:
``` py
import mara_superset.config

# the external URL for your superset instance
patch(mara_superset.config.external_superset_url)(lambda: 'https://external-superset-url.com/')

# the internal URL used for API calls
patch(mara_superset.config.internal_superset_url)(lambda: 'https://internal-superset-dns-name.local/')

# the api username and password
patch(mara_superset.config.metabase_api_username)(lambda: 'admin')
patch(mara_superset.config.metabase_api_password)(lambda: 'admin')

# the mara db alias for the database containing superset datasets
patch(mara_superset.config.superset_data_db_alias)(lambda: 'superset-data-read')

# the name of the database in Superset
patch(mara_superset.config.superset_data_db_name)(lambda: 'MyCompany DWH')

# the schema to be used for superset data sets
patch(mara_superset.config.superset_data_db_schema)(lambda: 'superset')
```

## Running Superset

Running `make run-superset` will start Apache Superset in a gunicorn app in console.

The default username is `admin` and the password `admin` as well.

## Features

### Metadata sync

If you have a data warehouse schema defined in [Mara Schema](https://github.com/mara/mara-schema), then you can automatically sync column descriptions and metric definitions with the update_metadata function in [mara_superset/metadata.py].

The database is created automatically. Datasets with their columns and metrics are synchronized after the data set table has been added manually via the UI. New columns are only added after executing the *Sync columns from Source* function via the Superset UI in the data set .
