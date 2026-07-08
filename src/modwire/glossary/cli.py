import click

from ..di import load_app
from .app import GlossaryApplication


@click.group()
@click.pass_context
def glossary(ctx):
    ctx.obj = ctx.find_root().obj


@glossary.command()
@click.pass_obj
def list_terms(container):
    app: GlossaryApplication = load_app(container, "glossary")
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
    container,
    term: str,
    definition: str,
    aliases: tuple[str, ...],
    relations: tuple[str, ...],
    sources: tuple[str, ...],
    parent_id: str,
):
    app: GlossaryApplication = load_app(container, "glossary")
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
    container,
    term_id: str,
    key: str,
    new_value: str,
):
    app: GlossaryApplication = load_app(container, "glossary")
    app.update_term_data(term_id, key, new_value)


@glossary.command()
@click.argument("term_id")
@click.argument("key")
@click.pass_obj
def remove_term_data(container, term_id: str, key: str):
    app: GlossaryApplication = load_app(container, "glossary")
    app.remove_term_data(term_id, key)


@glossary.command()
@click.argument("term_id")
@click.pass_obj
def remove_term(container, term_id: str):
    app: GlossaryApplication = load_app(container, "glossary")
    app.remove_term(term_id)
