from pathlib import Path

import click

from modwire.di import ModwireContainer, load_app

from .app import ScaffoldingApplication


@click.group()
@click.pass_context
def scaffolding(ctx):
    container: ModwireContainer = ctx.find_root().obj
    ctx.obj = load_app(container, "scaffolding")


@scaffolding.command()
@click.argument("name")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--data", "data_items", multiple=True)
@click.pass_obj
def generate(
    app: ScaffoldingApplication,
    name: str,
    destination: Path,
    data_items: tuple[str, ...],
):
    app.generate(name, destination, data_items)
    click.echo(f"Generated scaffold {name} at {destination}")
