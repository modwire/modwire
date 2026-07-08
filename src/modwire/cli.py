from pathlib import Path

import click
import modwire
import wireup
import wireup.integration.click

from .glossary.cli import glossary
from .projects.cli import projects
from .modules.cli import modules
from .layers.cli import layers
from .architecture.cli import architecture
from .scaffolding.cli import scaffolding
from .shared import ModwireContext


class ModwireGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except ValueError as error:
            raise click.ClickException(str(error)) from error


@click.group(cls=ModwireGroup)
@click.option(
    "--cwd",
    type=click.Path(path_type=Path, file_okay=False, dir_okay=True),
    default=None,
)
@click.pass_context
def cli(ctx, cwd: Path | None):
    _container.get(ModwireContext).cwd = (cwd or Path.cwd()).resolve()
    ctx.obj = _container


cli.add_command(glossary)
cli.add_command(projects)
cli.add_command(modules)
cli.add_command(layers)
cli.add_command(architecture)
cli.add_command(scaffolding)

_container = wireup.create_sync_container(injectables=[modwire])
wireup.integration.click.setup(_container, cli)


if __name__ == '__main__':
    cli()
