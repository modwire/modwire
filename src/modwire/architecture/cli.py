import click

from modwire.di import ModwireContainer, load_app

from .app import ArchitectureApplication


@click.group()
@click.pass_context
def architecture(ctx):
    container: ModwireContainer = ctx.find_root().obj
    ctx.obj = load_app(container, "architecture")


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
