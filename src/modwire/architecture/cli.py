import click

from modwire.shared import ModwireCLI

from .app import ArchitectureApplication
from .config import ArchitectureConfig


@click.group()
@click.pass_context
def architecture(ctx):
    modwire_cli: ModwireCLI = ctx.find_root().obj
    config = modwire_cli.load_config("architecture", ArchitectureConfig, "yaml")
    ctx.obj = ArchitectureApplication(config)


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
