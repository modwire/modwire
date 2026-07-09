from pathlib import Path

import click
from wireup import Injected

from ...architecture.app import ArchitectureApplication


@click.group()
def architecture():
    pass


@architecture.command()
def reports(app: Injected[ArchitectureApplication]):
    click.echo(app.reports().model_dump_json(indent=2))


@architecture.command()
@click.argument("root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("language")
def health(root: Path, language: str, app: Injected[ArchitectureApplication]):
    for report in app.report(root, language):
        click.echo(report.model_dump_json(indent=2))


@architecture.command()
def boundaries(app: Injected[ArchitectureApplication]):
    pass


@architecture.command()
def insights(app: Injected[ArchitectureApplication]):
    pass


@architecture.command()
def shape(app: Injected[ArchitectureApplication]):
    pass
