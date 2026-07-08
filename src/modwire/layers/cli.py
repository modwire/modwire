import click
from wireup import Injected

from .app import LayersApplication


@click.group()
def layers():
    pass


@layers.command()
@click.argument("name")
@click.argument("layout")
@click.argument("language")
def scaffold(
    name: str,
    layout: str,
    language: str,
    app: Injected[LayersApplication],
):
    pass

@layers.command()
@click.argument("name")
def remove_layer(name: str, app: Injected[LayersApplication]):
    pass


@layers.command()
@click.argument("name")
@click.argument("layer")
def add_package(name: str, layer: str, app: Injected[LayersApplication]):
    pass


@layers.command()
@click.argument("name")
@click.argument("layer")
def remove_package(name: str, layer: str, app: Injected[LayersApplication]):
    pass
