import click

from pathlib import Path

from .shared.base import ModwireCLI

from .projects.cli import projects
from .modules.cli import modules
from .layers.cli import layers
from .architecture.cli import architecture
from .scaffolding.cli import scaffolding


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
    ctx.obj = ModwireCLI(cwd or Path.cwd())


cli.add_command(projects)
cli.add_command(modules)
cli.add_command(layers)
cli.add_command(architecture)
cli.add_command(scaffolding)


if __name__ == '__main__':
    cli()
