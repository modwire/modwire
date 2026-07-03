import click

from .shared.base import ModwireCLI

from .projects.cli import projects
from .modules.cli import modules
from .layers.cli import layers
from .architecture.cli import architecture

from .shared.cli import tools


class ModwireGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except ValueError as error:
            raise click.ClickException(str(error)) from error


@click.group(cls=ModwireGroup)
@click.pass_context
def cli(ctx):
    ctx.obj = ModwireCLI()


cli.add_command(projects)
cli.add_command(modules)
cli.add_command(layers)
cli.add_command(architecture)
cli.add_command(tools)


if __name__ == '__main__':
    cli()
