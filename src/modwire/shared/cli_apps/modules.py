import click
from wireup import Injected

from ...modules.app import ModulesApplication


@click.group()
def modules():
    pass


@modules.command()
@click.argument("name")
def scaffold(name: str, app: Injected[ModulesApplication]):
    pass



@modules.command()
@click.argument("name")
def add_layer(name: str, app: Injected[ModulesApplication]):
    pass


@modules.command()
@click.argument("name")
def remove_layer(name: str, app: Injected[ModulesApplication]):
    pass


@modules.command()
@click.argument("name")
@click.argument("layer")
def add_package(name: str, layer: str, app: Injected[ModulesApplication]):
    pass


@modules.command()
@click.argument("name")
@click.argument("layer")
def remove_package(name: str, layer: str, app: Injected[ModulesApplication]):
    pass
