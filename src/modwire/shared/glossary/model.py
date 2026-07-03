from typing import List

from pydantic import Field

from modwire.shared import ModwireBaseModel

from .term import GlossaryTerm


class Glossary(ModwireBaseModel):
    terms: List[GlossaryTerm] = Field(default_factory=list)

    def render_text(self) -> str:
        lines = []

        for term in self.terms:
            lines.append(f"{term.term} ({term.aliases}), {term.term_id}")
            lines.append(term.definition)
            lines.append(str(term.sources))

        return "\n".join(lines)

    def render(self):
        text = self.render_text()
        if text:
            print(text)

    def add_term(
        self,
        term: str,
        definition: str,
        aliases: list[str],
        relations: list[str],
        sources: list[str],
        parent_id: str = "",
    ) -> tuple["Glossary", GlossaryTerm]:
        glossary_term = GlossaryTerm.create(
            term=term,
            definition=definition,
            aliases=aliases,
            relations=relations,
            sources=sources,
            parent_id=parent_id,
        )

        if any(existing.term_id == glossary_term.term_id for existing in self.terms):
            raise ValueError(f"Glossary term already exists: {glossary_term.term_id}")

        self._validate_parent(glossary_term)
        self._validate_relations(glossary_term)
        return self._set_terms([*self.terms, glossary_term]), glossary_term

    def update_term_data(self, term_id: str, key: str, new_value: str) -> "Glossary":
        term = self._find_term(term_id)
        updated_term = term.update_data(key, new_value)

        if key == "relations":
            self._validate_relations(updated_term)

        return self._replace_term(updated_term)

    def remove_term_data(self, term_id: str, key: str) -> "Glossary":
        term = self._find_term(term_id)
        return self._replace_term(term.remove_data(key))

    def remove_term(self, term_id: str) -> "Glossary":
        term = self._find_term(term_id)
        self._validate_can_remove(term)
        return self._set_terms(
            [existing for existing in self.terms if existing.term_id != term.term_id]
        )

    def _set_terms(self, terms: list[GlossaryTerm]) -> "Glossary":
        return self.model_copy(update={"terms": terms})

    def _find_term(self, term_id: str) -> GlossaryTerm:
        for term in self.terms:
            if term.term_id == term_id or term.id == term_id:
                return term
        raise ValueError(f"Glossary term does not exist: {term_id}")

    def _replace_term(self, updated_term: GlossaryTerm) -> "Glossary":
        return self._set_terms(
            [
                updated_term if term.term_id == updated_term.term_id else term
                for term in self.terms
            ]
        )

    def _term_ids(self) -> set[str]:
        return {term.term_id for term in self.terms}

    def _validate_parent(self, term: GlossaryTerm):
        if term.parent_id == term.id:
            return

        if term.parent_id not in self._term_ids():
            raise ValueError(f"Glossary parent does not exist: {term.parent_id}")

    def _validate_relations(self, term: GlossaryTerm):
        known_term_ids = self._term_ids()

        for relation in term.relations:
            if relation == term.term_id:
                raise ValueError(f"Glossary term cannot relate to itself: {term.term_id}")

            if relation not in known_term_ids:
                raise ValueError(f"Glossary relation does not exist: {relation}")

    def _validate_can_remove(self, term: GlossaryTerm):
        for existing in self.terms:
            if existing.term_id == term.term_id:
                continue

            if existing.parent_id == term.term_id:
                raise ValueError(
                    f"Glossary term has child terms and cannot be removed: {term.term_id}"
                )

            if term.term_id in existing.relations:
                raise ValueError(
                    "Glossary term is referenced by another term and cannot be "
                    f"removed: {term.term_id}"
                )
