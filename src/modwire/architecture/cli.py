import click

from .app import ArchitectureApplication
from .config import ArchitectureConfig


@click.group()
@click.pass_context
def architecture(ctx):
    ctx.obj = ArchitectureApplication()


@architecture.command()
@click.pass_obj
def boundaries(app: ArchitectureApplication):
    ...


@architecture.command()
@click.pass_obj
def insights(app: ArchitectureApplication):
    ...


@architecture.command()
@click.pass_obj
def shape(app: ArchitectureApplication):
    ...
