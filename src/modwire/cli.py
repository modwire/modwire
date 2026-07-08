import click
import wireup.integration.click

from .glossary.cli import glossary
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
@click.pass_context
def cli(ctx):
    ctx.obj = container


cli.add_command(glossary)
cli.add_command(projects)
cli.add_command(modules)
cli.add_command(layers)
cli.add_command(architecture)
cli.add_command(scaffolding)

from .app import container  # noqa: E402

wireup.integration.click.setup(container, cli)


if __name__ == '__main__':
    cli()
