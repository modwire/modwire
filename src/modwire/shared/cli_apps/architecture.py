from pathlib import Path

import click
from wireup import Injected

from ...architecture.app import ArchitectureApplication


@click.group()
def architecture():
    pass


@architecture.command()
@click.argument("root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("language")
def report(root: Path, language: str, app: Injected[ArchitectureApplication]):
    app.report(root, language)


@architecture.command()
def boundaries(app: Injected[ArchitectureApplication]):
    pass


@architecture.command()
def insights(app: Injected[ArchitectureApplication]):
    pass


@architecture.command()
def shape(app: Injected[ArchitectureApplication]):
    pass
