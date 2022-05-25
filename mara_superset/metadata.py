from enum import Flag, auto
from functools import singledispatch
import typing as t

import mara_db.dbs
import mara_schema.config
from mara_schema.data_set import DataSet
from mara_schema.entity import Entity
from mara_schema.metric import SimpleMetric, ComposedMetric, Aggregation, NumberFormat
from mara_schema.attribute import Attribute, Type

from . import config
from .client import SupersetClient


class UpdateStrategy(Flag):
    """
    The update strategy for metadata:

    CREATE  - when the model does not exist, create it
    UPDATE  - when the model exists, update its columns. Columns which where removed will be retained and return a 'NULL' value
    REPLACE - when the model exist, replace it.
    DELETE  - when a table exists but no model exists, delete it. SQL Views created in SQL Lab are not deleted.

    Suppgestion:
     - use CREATE | UPDATE in production environments
     - use only UPDATE in production environments where you want to control which models are exposed to the users.
     - use CREATE | REPLACE | DELETE in test, and staging and development environments
    """
    CREATE = auto()
    UPDATE = auto()
    REPLACE = auto()
    DELETE = auto()


def update_metadata(update_strategy: UpdateStrategy = None) -> bool:
    """
    Updates descriptions of tables & fields in Superset, creates metrics and flushes field caches
    
    Args:
        update_strategy: How the metadata should be updated. If not defined the value from config.metadata_update_strategy().
    """
    if not update_strategy:
        update_strategy = config.metadata_update_strategy()
    if not update_strategy:
        # no update strategy defined: do nothing and end with everything OK
        return True

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

    def create_raw_dataset_metadata(data_set: DataSet) -> int:
        response = client.post('/dataset/', data={
            'database': dwh_database_id,
            'schema': config.superset_data_db_schema(),
            'table_name': data_set.name
        })
        return response['id']

    def update_dataset_metadata(data_set: DataSet, data_set_id, create_null_columns: bool = True):
        _attributes: t.Dict[str, Attribute] = {}
        for path, attributes in data_set.connected_attributes().items():
            for name, attribute in attributes.items():
                _attributes[name] = attribute

        data_set_metadata_all = client.get(f'/dataset/{data_set_id}')['result']
        #print(data_set_metadata_all)

        data_set_columns = []

        for column in data_set_metadata_all.get('columns',[]):
            attribute = _attributes.get(column['column_name'], None)
            if attribute:
                data_set_columns.append({
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
                })
            elif create_null_columns:
                data_set_columns.append({
                    'id': column['id'],
                    'column_name': column['column_name'],
                    'description': '>> technical field hidden by schema sync',
                    'is_active': False,
                    'groupby': False
                })

        data_set_metrics = []

        for name, _metric in data_set.metrics.items():
            metric = {
                'metric_name': name,
                'description': superset_description(_metric),
                'expression': superset_metric_expression(_metric),
                'metric_type': 'metric', #None, -- 'count', None
                'd3format': superset_metric_d3format(_metric)
            }

            existing_metric = next(filter(lambda m: m['metric_name'] == name, data_set_metadata_all.get('metrics',[])), None)
            if existing_metric:
                metric['id'] = existing_metric['id']

            data_set_metrics.append(metric)

        client.put(f'/dataset/{data_set_id}', data={
            'description': superset_description(data_set.entity),
            'columns': data_set_columns,
            'metrics': data_set_metrics
        })

    def delete_dataset_metadata(data_set_id):
        client.delete(f'/dataset/{data_set_id}')

    data_sets = {data_set.name: data_set for data_set in mara_schema.config.data_sets()}
    DATASETS_METADATA_QUERY='/dataset/?q=(order_column:changed_on_delta_humanized,order_direction:desc,page:{0},page_size:{1},columns:!(id,schema,table_name),filters:!((col:schema,opr:eq,value:{2})))'
    PAGE_SIZE = 20
    datasets_page: int = 0
    datasets_iter_count: int = 0

    datasets_metadata = client.get(DATASETS_METADATA_QUERY.format(datasets_page, PAGE_SIZE, config.superset_data_db_schema()))
    datasets_count = datasets_metadata.get('count',0)

    while datasets_metadata.get('result'):
        datasets_iter_count += len(datasets_metadata['result'])
        for data_set_metadata in datasets_metadata['result']:
            #print(f"model: {data_set_metadata['table_name']}")
            data_set = data_sets.get(data_set_metadata['table_name'])
            if data_set:
                if bool(update_strategy & UpdateStrategy.UPDATE):
                    print(f'Update dataset "{data_set.name}" ...')
                    update_dataset_metadata(data_set, data_set_id=data_set_metadata["id"])
                elif bool(update_strategy & UpdateStrategy.REPLACE):
                    print(f'Replace dataset "{data_set.name}" ...')
                    delete_dataset_metadata(data_set_id=data_set_metadata["id"])
                    data_set_id = create_raw_dataset_metadata(data_set)
                    update_dataset_metadata(data_set, data_set_id=data_set_id)

                # removes the entity from the dict so we leave at the end only the
                # data sets in the dict which are not 
                del data_sets[data_set_metadata['table_name']]
            elif bool(update_strategy & UpdateStrategy.DELETE):
                if not data_set.get('is_sqllab_view',False):
                    delete_dataset_metadata(data_set_id=data_set_metadata["id"])

        # get next page if necessary
        if datasets_iter_count >= datasets_count:
            break
        datasets_page += 1
        datasets_metadata = client.get(DATASETS_METADATA_QUERY.format(datasets_page, PAGE_SIZE, config.superset_data_db_schema()))

    for data_set in data_sets.values():
        if bool(update_strategy & UpdateStrategy.CREATE):
            print(f'Create dataset "{data_set.name}" ...')
            data_set_id = create_raw_dataset_metadata(data_set)
            update_dataset_metadata(data_set, data_set_id=data_set_id)
        else:
            print(f'[NOTE] The data set {data_set.name} does not exist in Superset and will not be created because of the used update strategy.')

    return True


def superset_description(entity: t.Union[Entity, SimpleMetric, ComposedMetric, Attribute]):
    """Returns the description of the item"""
    return entity.description


def superset_metric_expression(metric: t.Union[SimpleMetric, ComposedMetric]):
    """Turn a Mara Schema metric into a a sql formula"""

    if isinstance(metric, SimpleMetric):
        if metric.aggregation == Aggregation.DISTINCT_COUNT:
            return f'COUNT(DISTINCT "{metric.name}")'
        else:
            return f'{str(metric.aggregation).upper()}("{metric.name}")'

    elif isinstance(metric, ComposedMetric):
        return metric.formula_template.format(
            *[f'({superset_metric_expression(metric)})' for metric in metric.parent_metrics])

    else:
        assert False


def superset_metric_d3format(metric: t.Union[SimpleMetric, ComposedMetric]) -> str:
    """
    Turns the metric number format into a D3 format.

    See: https://github.com/d3/d3-format
    """
    if metric.number_format == NumberFormat.STANDARD:
        return ',.2s'
    elif metric.number_format == NumberFormat.CURRENCY:
        return '$,.2f'
    elif metric.number_format == NumberFormat.PERCENT:
        return ',.2f%'
    else:
        return None


# To see supported drivers by Apache Superset see:
# https://superset.apache.org/docs/databases/installing-database-drivers/

@singledispatch
def db_backend_name(db) -> str:
    """Returns the db backend name for a mara db alias"""
    raise NotImplementedError(f'Please implement db_backend_name for type "{db.__class__.__name__}"')

@db_backend_name.register(str)
def __(db: str):
    return db_backend_name(mara_db.dbs.db(db))

@db_backend_name.register(mara_db.dbs.PostgreSQLDB)
def __(db):
    return 'postgresql'

#@db_backend_name.register(mara_db.dbs.RedshiftDB)
#def __(db):
#    return 'redshift'

#@db_backend_name.register(mara_db.dbs.BigQueryDB)
#def __(db):
#    return 'bigquery'

#@db_backend_name.register(mara_db.dbs.MysqlDB)
#def __(db):
#    return 'mysql'

@db_backend_name.register(mara_db.dbs.SQLServerDB)
def __(db):
    return 'mssql'

#@db_backend_name.register(mara_db.dbs.OracleDB)
#def __(db):
#    return 'oracle'

@db_backend_name.register(mara_db.dbs.SQLiteDB)
def __(db):
    return 'sqlite'


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

@sqlalchemy_url.register(mara_db.dbs.SQLServerDB)
def __(db):
    port = db.port if db.port else 1433
    driver = db.odbc_driver.replace(' ','+')
    return (f'mssql+pyodbc://{db.user}:{db.password}@{db.host}:{port}/{db.database}?driver={driver}'
            + ('&TrustServerCertificate=yes' if db.trust_server_certificate else ''))

@sqlalchemy_url.register(mara_db.dbs.SQLiteDB)
def __(db: mara_db.dbs.SQLiteDB):
    return f'sqlite:///{db.file_name}'
