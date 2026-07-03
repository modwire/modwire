import click

from .app import ModulesApplication


@click.group()
@click.pass_context
def modules(ctx):
    ctx.obj = ModulesApplication()


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
