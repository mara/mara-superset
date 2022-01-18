from functools import singledispatch
import sys
import typing as t

import mara_db.dbs
import mara_schema.config
from mara_schema.entity import Entity
from mara_schema.metric import Metric, SimpleMetric, ComposedMetric, Aggregation
from mara_schema.attribute import Attribute, Type

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

    datasets_metadata = client.get('/dataset/')
    data_sets = {data_set.name: data_set for data_set in mara_schema.config.data_sets()}

    for data_set_metadata in datasets_metadata.get('result',[]):
        if str(data_set_metadata['schema']).lower() == config.superset_data_db_schema().lower():
            data_set = data_sets.get(data_set_metadata['table_name'])
            if data_set:
                _attributes: t.Dict[str, Attribute] = {}
                for path, attributes in data_set.connected_attributes().items():
                    for name, attribute in attributes.items():
                        _attributes[name] = attribute

                data_set_metadata_all = client.get(f'/dataset/{data_set_metadata["id"]}')['result']
                #print(data_set_metadata_all)

                data_set_columns = []

                for column in data_set_metadata_all.get('columns',[]):
                    attribute = _attributes.get(column['column_name'], None)
                    if attribute:
                        new_column = {
                            'id': column['id'],
                            'column_name': column['column_name'],
                            'description': superset_description(attribute) or 'tbd',
                            #'filterable': column.get('filterable',True),
                            'groupby': True,
                            'is_active': True,
                            'is_dttm': attribute.type == Type.DATE,
                            #'python_date_format': column.get('python_date_format',True),
                            #'type': column.get('type',True),
                            'verbose_name': column['column_name']
                        }
                    else:
                        new_column = {
                            'id': column['id'],
                            'column_name': column['column_name'],
                            'description': '>> technical field hidden by schema sync',
                            'is_active': False,
                            'groupby': False
                        }

                    data_set_columns.append(new_column)

                data_set_metrics = []

                for name, _metric in data_set.metrics.items():
                    metric = {'metric_name': name,
                              'description': superset_description(_metric),
                              'expression': superset_metric_expression(_metric),
                              'metric_type': 'metric', #None, -- 'count', None
                              }

                    existing_metric = next(filter(lambda m: m['metric_name'] == name, data_set_metadata_all.get('metrics',[])), None)
                    if existing_metric:
                        metric['id'] = existing_metric['id']

                    data_set_metrics.append(metric)

                client.put(f'/dataset/{data_set_metadata["id"]}', data={
                    'description': superset_description(data_set.entity),
                    'columns': data_set_columns,
                    'metrics': data_set_metrics
                })


def superset_description(entity: t.Union[Entity, SimpleMetric, ComposedMetric, Attribute]):
    """Returns the description of ths item"""
    return entity.description


def superset_metric_expression(metric: t.Union[SimpleMetric, ComposedMetric]):
    """Turn a Mara Schema metric into a a sql formula"""

    if isinstance(metric, SimpleMetric):
        if metric.aggregation == Aggregation.SUM:
            return f'SUM("{metric.name}")'
        elif metric.aggregation == Aggregation.AVERAGE:
            return f'AVG("{metric.name}")'
        elif metric.aggregation == Aggregation.COUNT:
            return f'COUNT("{metric.name}")'
        elif metric.aggregation == Aggregation.DISTINCT_COUNT:
            return f'COUNT(DISTINCT "{metric.name}")'

    elif isinstance(metric, ComposedMetric):
        return metric.formula_template.format(
            *[f'({superset_metric_expression(metric)})' for metric in metric.parent_metrics])

    else:
        assert False


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
