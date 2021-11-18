import flask
from mara_page import acl, navigation

blueprint = flask.Blueprint('mara_superset', __name__, url_prefix='/')


acl_resource = acl.AclResource(name='Superset')


def navigation_entry():
    return navigation.NavigationEntry(
        label='Superset', uri_fn=lambda: flask.url_for('mara_superset.superset'),
        icon='bar-chart', description='Superset website')



@blueprint.route('/superset')
@acl.require_permission(acl_resource)
def superset():
    from . import config

    return flask.redirect(config.external_superset_url())