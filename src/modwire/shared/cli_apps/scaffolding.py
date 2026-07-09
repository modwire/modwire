from pathlib import Path

import click
from wireup import Injected

from ..console import parse_inputs
from ..scaffolding.app import ScaffoldingApplication


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
    data = parse_inputs(data_items)
    for key in app.required_data_keys(name):
        if key not in data:
            data[key] = click.prompt(key)

    app.generate(name, destination, data)
    click.echo(f"Generated scaffold {name} at {destination}")
