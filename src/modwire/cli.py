import click
import wireup.integration.click

from modwire.shared.config import ModwireConfig

from .shared import cli_apps, create_application


@click.group(invoke_without_command=True, no_args_is_help=False)
@click.pass_context
def cli(ctx):
    application = create_application(ModwireConfig())
    wireup.integration.click.setup(application.container, cli)
    
    ctx.obj = application.container
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


cli.add_command(cli_apps.glossary)
cli.add_command(cli_apps.scaffolding)
cli.add_command(cli_apps.projects)
cli.add_command(cli_apps.modules)
cli.add_command(cli_apps.layers)
cli.add_command(cli_apps.architecture)


if __name__ == "__main__":
    cli()
