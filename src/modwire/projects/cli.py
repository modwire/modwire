import click

from ..di import load_app


@click.group()
@click.pass_context
def projects(ctx):
    ctx.obj = ctx.find_root().obj


@projects.command()
@click.argument("name")
@click.argument("root")
@click.pass_obj
def init(container, name: str, root: str):
    app = load_app(container, "projects")



@projects.command()
@click.argument("names")
@click.argument("group")
@click.pass_obj
def add_dependencies(container, names: list[str], group: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("names")
@click.argument("group")
@click.pass_obj
def remove_dependencies(container, names: list[str], group: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.pass_obj
def add_module(container, name: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.pass_obj
def remove_module(container, name: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.argument("module")
@click.pass_obj
def add_layer(container, name: str, module: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.argument("module")
@click.pass_obj
def remove_layer(container, name: str, module: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.argument("module")
@click.argument("layer")
@click.pass_obj
def add_package(container, name: str, module: str, layer: str):
    app = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.argument("module")
@click.argument("layer")
@click.pass_obj
def remove_package(container, name: str, module: str, layer: str):
    app = load_app(container, "projects")
