from wireup import injectable

from modwire.shared import ModwireBaseApplication

from .services import GlossaryRenderer, GlossaryRepository, GlossaryTerm


@injectable(lifetime="transient")
class GlossaryApplication(ModwireBaseApplication):
    def __init__(
        self,
        repository: GlossaryRepository,
        renderer: GlossaryRenderer,
    ):
        self._repository = repository
        self._renderer = renderer

    def run(self):
        self.list_terms()

    def list_terms(self):
        glossary = self._repository.load()
        self._renderer.render(glossary)

    def add_term(
        self,
        term: str,
        definition: str,
        aliases: list[str],
        relations: list[str],
        sources: list[str],
        parent_id: str = "",
    ) -> GlossaryTerm:
        glossary = self._repository.load()
        glossary, glossary_term = glossary.add_term(
            term=term,
            definition=definition,
            aliases=aliases,
            relations=relations,
            sources=sources,
            parent_id=parent_id,
        )
        self._repository.save(glossary)
        return glossary_term

    def update_term_data(self, term_id: str, key: str, new_value: str) -> None:
        glossary = self._repository.load()
        glossary = glossary.update_term_data(term_id, key, new_value)
        self._repository.save(glossary)

    def remove_term_data(self, term_id: str, key: str) -> None:
        glossary = self._repository.load()
        glossary = glossary.remove_term_data(term_id, key)
        self._repository.save(glossary)

    def remove_term(self, term_id: str) -> None:
        glossary = self._repository.load()
        glossary = glossary.remove_term(term_id)
        self._repository.save(glossary)
