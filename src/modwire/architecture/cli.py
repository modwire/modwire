import click

from ..di import load_app


@click.group()
@click.pass_context
def architecture(ctx):
    ctx.obj = ctx.find_root().obj


@architecture.command()
@click.pass_obj
def boundaries(container):
    app = load_app(container, "architecture")


@architecture.command()
@click.pass_obj
def insights(container):
    app = load_app(container, "architecture")


@architecture.command()
@click.pass_obj
def shape(container):
    app = load_app(container, "architecture")
