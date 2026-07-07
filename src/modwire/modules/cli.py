import click

from modwire.di import ModwireContainer, load_app

from .app import ModulesApplication


@click.group()
@click.pass_context
def modules(ctx):
    container: ModwireContainer = ctx.find_root().obj
    ctx.obj = load_app(container, "modules")


@modules.command()
@click.argument("name")
@click.argument("target")
@click.pass_obj
def scaffold(app: ModulesApplication, name: str):
    pass


@modules.command()
@click.argument("name")
@click.pass_obj
def add_layer(app: ModulesApplication, name: str):
    pass


@modules.command()
@click.argument("name")
@click.pass_obj
def remove_layer(app: ModulesApplication, name: str):
    pass


@modules.command()
@click.argument("name")
@click.argument("layer")
@click.pass_obj
def add_package(app: ModulesApplication, name: str, layer: str):
    pass


@modules.command()
@click.argument("name")
@click.argument("layer")
@click.pass_obj
def remove_package(app: ModulesApplication, name: str, layer: str):
    pass
