import click
import wireup.integration.click

from modwire.shared.config import ModwireConfig

from .app import create_application
from .architecture.cli import architecture
from .layers.cli import layers
from .modules.cli import modules
from .projects.cli import projects
from .shared.glossary.cli import glossary
from .shared.scaffolding.cli import scaffolding


application = create_application(ModwireConfig())


class ModwireGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except ValueError as error:
            raise click.ClickException(str(error)) from error


@click.group(cls=ModwireGroup, invoke_without_command=True, no_args_is_help=False)
@click.pass_context
def cli(ctx):
    ctx.obj = application.container

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


cli.add_command(glossary)
cli.add_command(scaffolding)
cli.add_command(projects)
cli.add_command(modules)
cli.add_command(layers)
cli.add_command(architecture)

wireup.integration.click.setup(application.container, cli)


if __name__ == "__main__":
    cli()
