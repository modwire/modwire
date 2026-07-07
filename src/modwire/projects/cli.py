import click

from modwire.di import ModwireContainer, load_app

from .app import ProjectsApplication


@click.group()
@click.pass_context
def projects(ctx):
    container: ModwireContainer = ctx.find_root().obj
    ctx.obj = load_app(container, "projects")


@projects.command()
@click.argument("name")
@click.argument("root")
@click.pass_obj
def init(app: ProjectsApplication, name: str, root: str):
    pass


@projects.command()
@click.argument("names")
@click.argument("group")
@click.pass_obj
def add_dependencies(app: ProjectsApplication, names: list[str], group: str):
    pass


@projects.command()
@click.argument("names")
@click.argument("group")
@click.pass_obj
def remove_dependencies(app: ProjectsApplication, names: list[str], group: str):
    pass


@projects.command()
@click.argument("name")
@click.pass_obj
def add_module(app: ProjectsApplication, name: str):
    pass


@projects.command()
@click.argument("name")
@click.pass_obj
def remove_module(app: ProjectsApplication, name: str):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
@click.pass_obj
def add_layer(app: ProjectsApplication, name: str, module: str):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
@click.pass_obj
def remove_layer(app: ProjectsApplication, name: str, module: str):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
@click.argument("layer")
@click.pass_obj
def add_package(app: ProjectsApplication, name: str, module: str, layer: str):
    pass


@projects.command()
@click.argument("name")
@click.argument("module")
@click.argument("layer")
@click.pass_obj
def remove_package(app: ProjectsApplication, name: str, module: str, layer: str):
    pass
