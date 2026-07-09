from pathlib import Path

import click
from wireup import Injected

from ...architecture.app import ArchitectureApplication


class ArchitectureGroup(click.Group):
    def resolve_command(self, ctx: click.Context, args: list[str]):
        if args and self.get_command(ctx, args[0]) is None and Path(args[0]).is_dir():
            report_command = self.get_command(ctx, "report")
            if report_command is not None:
                return "report", report_command, args

        return super().resolve_command(ctx, args)


@click.group(cls=ArchitectureGroup)
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
