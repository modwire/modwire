from pathlib import Path

import click
from wireup import Injected

from ..cli import parse_inputs
from .app import ScaffoldingApplication


@click.group()
def scaffolding():
    pass


@scaffolding.command()
@click.argument("name")
@click.argument("destination", type=click.Path(path_type=Path))
@click.option("--data", "data_items", multiple=True)
def generate(
    name: str,
    destination: Path,
    data_items: tuple[str, ...],
    app: Injected[ScaffoldingApplication],
):
    app.generate(name, destination, parse_inputs(data_items))
    click.echo(f"Generated scaffold {name} at {destination}")
