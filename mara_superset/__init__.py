__version__ = '1.0.3'

def MARA_CONFIG_MODULES():
    from . import config
    return [config]

def MARA_FLASK_BLUEPRINTS():
    from . import views
    return [views.blueprint]

def MARA_CLICK_COMMANDS():
    from . import cli
    return [cli.update_metadata]

def MARA_ACL_RESOURCES():
    from .views import acl_resource
    return {'Superset': acl_resource}

def MARA_NAVIGATION_ENTRIES():
    from . import views
    return {'Superset': views.navigation_entry()}