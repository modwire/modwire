import click

from wireup import Injected

from ...projects.app import ProjectsApplication


@click.group()
def projects():
    pass


@projects.command()
@click.argument("name")
@click.argument("root")
def init(
    name: str, 
    root: str, 
    app: Injected[ProjectsApplication]
):
    pass


@projects.command()
@click.argument("names")
@click.argument("group")
def add_dependencies(
    names: list[str],
    group: str,
    app: Injected[ProjectsApplication],
):
    pass


@projects.command()
@click.argument("names")
@click.argument("group")
def remove_dependencies(
    names: list[str],
    group: str,
    app: Injected[ProjectsApplication],
):
    pass


@projects.command()
@click.argument("name")
def add_module(name: str, app: Injected[ProjectsApplication]):
    pass


@projects.command()
@click.argument("name")
def remove_module(name: str, app: Injected[ProjectsApplication]):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
def add_layer(name: str, module: str, app: Injected[ProjectsApplication]):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
def remove_layer(name: str, module: str, app: Injected[ProjectsApplication]):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
@click.argument("layer")
def add_package(
    name: str,
    module: str,
    layer: str,
    app: Injected[ProjectsApplication],
):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
@click.argument("layer")
def remove_package(
    name: str,
    module: str,
    layer: str,
    app: Injected[ProjectsApplication],
):
    pass
