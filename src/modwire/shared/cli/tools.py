import click

from .glossary import glossary
from .scaffolding import scaffolding


@click.group()
@click.pass_context
def tools(ctx):
    pass


tools.add_command(glossary)
tools.add_command(scaffolding)
