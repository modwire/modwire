import click
from wireup import Injected

from ..glossary.app import GlossaryApplication


@click.group()
def glossary():
    pass


@glossary.command()
def list_terms(app: Injected[GlossaryApplication]):
    app.list_terms()


@glossary.command()
@click.argument("term")
@click.option("--definition", "-d", prompt=True)
@click.option("--alias", "aliases", multiple=True)
@click.option("--relation", "relations", multiple=True)
@click.option("--source", "sources", multiple=True)
@click.option("--parent-id", default="")
def add_term(
    term: str,
    definition: str,
    aliases: tuple[str, ...],
    relations: tuple[str, ...],
    sources: tuple[str, ...],
    parent_id: str,
    app: Injected[GlossaryApplication],
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
def update_term_data(
    term_id: str,
    key: str,
    new_value: str,
    app: Injected[GlossaryApplication],
):
    app.update_term_data(term_id, key, new_value)


@glossary.command()
@click.argument("term_id")
@click.argument("key")
def remove_term_data(
    term_id: str,
    key: str,
    app: Injected[GlossaryApplication],
):
    app.remove_term_data(term_id, key)


@glossary.command()
@click.argument("term_id")
def remove_term(term_id: str, app: Injected[GlossaryApplication]):
    app.remove_term(term_id)
