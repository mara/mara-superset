"""Apache Superset API integration"""


def external_superset_url():
    """The URL under which the Superset instance can be reached by users e.g. https://superset.bi.example.com"""
    return 'http://localhost:8088'


def internal_superset_url():
    """The URL under which the Superset instance can be reached by from mara (usually circumventing SSOs etc.)"""
    return 'http://localhost:8088'


def metabase_api_username() -> str:
    """The email of the user for accessing the superset api"""
    return 'admin'

def metabase_api_password():
    """The password of the user for accessing the superset api"""
    return 'admin'


def superset_metadata_db_alias() -> str:
    """The db alias of the Superset metadata database"""
    return 'superset-metadata'


def superset_data_db_alias() -> str:
    """The alias of the database that Superset reads data from"""
    return 'superset-data-read'


def superset_data_db_name() -> str:
    """The name (in Superset) of the database that Superset reads from"""
    return 'MyCompany DWH'
