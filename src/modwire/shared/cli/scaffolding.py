from pathlib import Path

import click

from ..scaffolding import ScaffoldingApplication


@click.group()
@click.pass_context
def scaffolding(ctx):
    ctx.obj = ScaffoldingApplication(Path.cwd())


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
    app.generate_from_data_items(name, destination, data_items)
    click.echo(f"Generated scaffold {name} at {destination}")
