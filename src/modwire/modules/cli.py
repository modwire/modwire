import click

from ..di import load_app


@click.group()
@click.pass_context
def modules(ctx):
    ctx.obj = ctx.find_root().obj


@modules.command()
@click.argument("name")
@click.pass_obj
def scaffold(container, name: str):
    app = load_app(container, "modules")



@modules.command()
@click.argument("name")
@click.pass_obj
def add_layer(container, name: str):
    app = load_app(container, "modules")


@modules.command()
@click.argument("name")
@click.pass_obj
def remove_layer(container, name: str):
    app = load_app(container, "modules")


@modules.command()
@click.argument("name")
@click.argument("layer")
@click.pass_obj
def add_package(container, name: str, layer: str):
    app = load_app(container, "modules")


@modules.command()
@click.argument("name")
@click.argument("layer")
@click.pass_obj
def remove_package(container, name: str, layer: str):
    app = load_app(container, "modules")
