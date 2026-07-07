import click

from modwire.di import ModwireContainer, load_app

from .app import LayersApplication


@click.group()
@click.pass_context
def layers(ctx):
    container: ModwireContainer = ctx.find_root().obj
    ctx.obj = load_app(container, "layers")


@layers.command()
@click.argument("name")
@click.argument("layout")
@click.argument("language")
@click.pass_obj
def scaffold(app: LayersApplication, name: str, layout: str, language: str, target: str):
    pass

@layers.command()
@click.argument("name")
@click.pass_obj
def remove_layer(app: LayersApplication, name: str):
    pass


@layers.command()
@click.argument("name")
@click.argument("layer")
@click.pass_obj
def add_package(app: LayersApplication, name: str, layer: str):
    pass


@layers.command()
@click.argument("name")
@click.argument("layer")
@click.pass_obj
def remove_package(app: LayersApplication, name: str, layer: str):
    pass
