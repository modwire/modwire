import click
from wireup import Injected

from .app import ArchitectureApplication


@click.group()
def architecture():
    pass


@architecture.command()
def boundaries(app: Injected[ArchitectureApplication]):
    pass


@architecture.command()
def insights(app: Injected[ArchitectureApplication]):
    pass


@architecture.command()
def shape(app: Injected[ArchitectureApplication]):
    pass
