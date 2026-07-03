from pathlib import Path

from .model import Glossary
from .term import GlossaryTerm


class GlossaryApplication:
    def __init__(self, root: Path):
        self._root = root
        self._file = root / "glossary.json"
        self._glossary = Glossary()

        if self._file.exists():
            self._glossary = Glossary.load_json(self._file)

    def list_terms(self):
        self._glossary.render()

    def _save(self):
        self._glossary.save_json(self._file)

    def add_term(
        self,
        term: str,
        definition: str,
        aliases: list[str],
        relations: list[str],
        sources: list[str],
        parent_id: str = "",
    ) -> GlossaryTerm:
        self._glossary, glossary_term = self._glossary.add_term(
            term=term,
            definition=definition,
            aliases=aliases,
            relations=relations,
            sources=sources,
            parent_id=parent_id,
        )
        self._save()
        return glossary_term

    def update_term_data(self, term_id: str, key: str, new_value: str) -> None:
        self._glossary = self._glossary.update_term_data(term_id, key, new_value)
        self._save()

    def remove_term_data(self, term_id: str, key: str) -> None:
        self._glossary = self._glossary.remove_term_data(term_id, key)
        self._save()

    def remove_term(self, term_id: str) -> None:
        self._glossary = self._glossary.remove_term(term_id)
        self._save()
