import click

import wireup.integration.click

from .shared.glossary.cli import glossary
from .shared.scaffolding.cli import scaffolding
from .projects.cli import projects
from .modules.cli import modules
from .layers.cli import layers
from .architecture.cli import architecture
from .app import container


class ModwireGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except ValueError as error:
            raise click.ClickException(str(error)) from error


@click.group(cls=ModwireGroup, invoke_without_command=True, no_args_is_help=False)
@click.pass_context
def cli(ctx):
    ctx.obj = container
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


cli.add_command(glossary)
cli.add_command(scaffolding)
cli.add_command(projects)
cli.add_command(modules)
cli.add_command(layers)
cli.add_command(architecture)


wireup.integration.click.setup(container, cli)


if __name__ == '__main__':
    cli()
