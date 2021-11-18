#import sys
#import time
import typing as t
from functools import singledispatch

import mara_db.dbs
#import mara_schema.config
#from mara_schema.metric import Metric, SimpleMetric, ComposedMetric, Aggregation
#from mara_schema.attribute import Attribute

from . import config
from .client import SupersetClient


def update_metadata() -> bool:
    """Updates descriptions of tables & fields in Superset, creates metrics and flushes field caches"""
    client = SupersetClient()

    dwh_database_id = \
        next(filter(lambda db: db['database_name'] == config.superset_data_db_name(),
                    client.get('/database/')['result']),
            {}).get('id')

    if not dwh_database_id:
        print('DWH Database not found, create it ...')

        backend_name = db_backend_name(config.superset_data_db_alias())
        sqlalchem_url = sqlalchemy_url(config.superset_data_db_alias())

        result = client.post('/database/', data={
            "allow_csv_upload": False,
            "allow_ctas": False,
            "allow_cvas": False,
            "allow_dml": False,
            "allow_multi_schema_metadata_fetch": False,
            "allow_run_async": False,
            "backend": backend_name,
            "cache_timeout": None,
            "configuration_method": "sqlalchemy_form",
            "database_name": config.superset_data_db_name(),
            #"encrypted_extra": "string",
            #"engine": "string",
            #"expose_in_sqllab": True,
            "extra": "{\"metadata_params\":{},\"engine_params\":{},\"metadata_cache_timeout\":{},\"schemas_allowed_for_csv_upload\":[]}",
            "force_ctas_schema": None,
            "impersonate_user": False,
            "parameters": {},
            #"server_cert": "string",
            "sqlalchemy_uri": sqlalchem_url
        })
        dwh_database_id = result.get('id')

        if not dwh_database_id:
            raise Exception('Could not get the id from the newly created Database!')

    # TODO: sync. the datasets like it is done for metabase here: https://github.com/mara/mara-metabase/blob/master/mara_metabase/metadata.py


@singledispatch
def db_backend_name(db) -> str:
    """Returns the db backend name for a mara db alias"""
    raise NotImplementedError(f'Please implement db_backend_name for type "{db.__class__.__name__}"')

@db_backend_name.register(str)
def __(db: str):
    return db_backend_name(mara_db.dbs.db(db))

@db_backend_name.register(mara_db.dbs.SQLiteDB)
def __(db):
    return 'sqlite'

@db_backend_name.register(mara_db.dbs.SQLServerDB)
def __(db):
    return 'mssql'


@singledispatch
def sqlalchemy_url(db):
    """Returns the sqlalchemy url for a mara db alias"""
    raise NotImplementedError(f'Please implement sqlalchemy_url for type "{db.__class__.__name__}"')

@sqlalchemy_url.register(str)
def __(db: str):
    return sqlalchemy_url(mara_db.dbs.db(db))

@sqlalchemy_url.register(mara_db.dbs.PostgreSQLDB)
def __(db: mara_db.dbs.PostgreSQLDB):
    return f'postgresql+psycopg2://{db.user}{":" + db.password if db.password else ""}@{db.host}' \
        + f'{":" + str(db.port) if db.port else ""}/{db.database}'


#@sqlalchemy_url.register(mara_db.dbs.BigQueryDB)
#def __(db: mara_db.dbs.BigQueryDB):
#    # creates bigquery dialect
#    url = 'bigquery://'
#    if db.project:
#        url += db.project
#        if db.dataset:
#            url += '/' + db.dataset
#
#    return sqlalchemy.create_engine(url,
#                                    credentials_path=db.service_account_json_file_name,
#                                    location=db.location)


@sqlalchemy_url.register(mara_db.dbs.SQLiteDB)
def __(db: mara_db.dbs.SQLiteDB):
    return f'sqlite:///{db.file_name}'

@sqlalchemy_url.register(mara_db.dbs.SQLServerDB)
def __(db):
    port = db.port if db.port else 1433
    driver = db.odbc_driver.replace(' ','+')
    return f'mssql+pyodbc://{db.user}:{db.password}@{db.host}:{port}/{db.database}?driver={driver}'
