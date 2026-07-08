from pathlib import Path

import click

from ..shared.cli import parse_inputs

from ..di import load_app


@click.group()
@click.pass_context
def scaffolding(ctx):
    ctx.obj = ctx.find_root().obj


@scaffolding.command()
@click.argument("name")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--data", "data_items", multiple=True)
@click.pass_obj
def generate(
    container,
    name: str,
    destination: Path,
    data_items: tuple[str, ...],
):
    app = load_app(container, "scaffolding")
    app.generate(name, destination, parse_inputs(data_items))
    click.echo(f"Generated scaffold {name} at {destination}")
