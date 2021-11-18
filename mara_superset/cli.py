import click


@click.command()
def update_metadata():
    """Sync schema definitions from Mara to Superset"""
    from . import metadata
    metadata.update_metadata()