"""Apache Superset API integration"""


def external_superset_url():
    """The URL under which the Superset instance can be reached by users e.g. https://superset.bi.example.com"""
    return 'http://localhost:8088'


def internal_superset_url():
    """The URL under which the Superset instance can be reached by from mara (usually circumventing SSOs etc.)"""
    return 'http://localhost:8088'


def superset_api_username() -> str:
    """The email of the user for accessing the superset api"""
    return 'admin'

def superset_api_password():
    """The password of the user for accessing the superset api"""
    return 'admin'


def superset_data_db_alias() -> str:
    """The alias of the database that Superset reads data from"""
    return 'superset-data-read'

def superset_data_db_name() -> str:
    """The name (in Superset) of the database that Superset reads from"""
    return 'MyCompany DWH'

def superset_data_db_schema() -> str:
    """The name of the schema where the flattered data sets for Superset are stored"""
    return 'superset'

def metadata_update_strategy():
    """The default update strategy to be used when synchronizing metadata"""
    from .metadata import UpdateStrategy
    return UpdateStrategy.CREATE | UpdateStrategy.UPDATE
