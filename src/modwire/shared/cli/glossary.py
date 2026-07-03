from pathlib import Path

import click

from ..glossary import GlossaryApplication


@click.group()
@click.pass_context
def glossary(ctx):
    ctx.obj = GlossaryApplication(Path.cwd())


@glossary.command()
@click.pass_obj
def list_terms(app: GlossaryApplication):
    app.list_terms()


@glossary.command()
@click.argument("term")
@click.option("--definition", "-d", prompt=True)
@click.option("--alias", "aliases", multiple=True)
@click.option("--relation", "relations", multiple=True)
@click.option("--source", "sources", multiple=True)
@click.option("--parent-id", default="")
@click.pass_obj
def add_term(
    app: GlossaryApplication,
    term: str,
    definition: str,
    aliases: tuple[str, ...],
    relations: tuple[str, ...],
    sources: tuple[str, ...],
    parent_id: str,
):
    glossary_term = app.add_term(
        term=term,
        definition=definition,
        aliases=list(aliases),
        relations=list(relations),
        sources=list(sources),
        parent_id=parent_id,
    )
    click.echo(f"Added glossary term: {glossary_term.term_id}")


@glossary.command()
@click.argument("term_id")
@click.argument("key")
@click.argument("new_value")
@click.pass_obj
def update_term_data(
    app: GlossaryApplication,
    term_id: str,
    key: str,
    new_value: str,
):
    app.update_term_data(term_id, key, new_value)


@glossary.command()
@click.argument("term_id")
@click.argument("key")
@click.pass_obj
def remove_term_data(app: GlossaryApplication, term_id: str, key: str):
    app.remove_term_data(term_id, key)


@glossary.command()
@click.argument("term_id")
@click.pass_obj
def remove_term(app: GlossaryApplication, term_id: str):
    app.remove_term(term_id)
