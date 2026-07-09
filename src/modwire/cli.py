from pathlib import Path

import click

import wireup.integration.click

from .shared import cli_apps, create_application, ModwireConfig


@click.group(invoke_without_command=True, no_args_is_help=False)
@click.option(
    "--config-dir",
    "-d",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory containing Modwire YAML config files.",
)
@click.pass_context
def cli(ctx, config_dir: Path | None):
    config = ModwireConfig.load_dir(config_dir) if config_dir else ModwireConfig()
    application = create_application(config)
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
