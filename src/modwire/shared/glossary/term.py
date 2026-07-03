from typing import Any, List

from pydantic import AnyUrl, Field

from modwire.shared import ModwireBaseModel

from .utils import IDENTITY_FIELDS, REQUIRED_FIELDS, deduplicate, slug


class GlossaryTerm(ModwireBaseModel):
    id: str  # slug identifier
    parent_id: str  # if at the top, parent_id = id, else parent item
    term: str
    definition: str = Field(..., min_length=10)
    aliases: List[str] = Field(default_factory=list)
    relations: List[str] = Field(default_factory=list)  # existing term ids
    sources: List[AnyUrl] = Field(default_factory=list)  # may reference local file

    @property
    def term_id(self) -> str:
        if self.parent_id == self.id:
            return self.id
        return f"{self.parent_id}.{self.id}"

    @classmethod
    def create(
        cls,
        term: str,
        definition: str,
        aliases: list[str],
        relations: list[str],
        sources: list[str],
        parent_id: str = "",
    ) -> "GlossaryTerm":
        term_id = slug(term)
        if not term_id:
            raise ValueError("Term must contain at least one letter or number.")

        return cls(
            id=term_id,
            parent_id=parent_id or term_id,
            term=term,
            definition=definition,
            aliases=deduplicate(aliases),
            relations=deduplicate(relations),
            sources=deduplicate(sources),
        )

    def update_data(self, key: str, new_value: str) -> "GlossaryTerm":
        if key in IDENTITY_FIELDS:
            raise ValueError(f"Glossary term field cannot be updated: {key}")

        data, current_value = self._field_data(key)
        value = (
            deduplicate([*current_value, new_value])
            if isinstance(current_value, list)
            else new_value
        )
        return self._with_field(data, key, value)

    def remove_data(self, key: str) -> "GlossaryTerm":
        if key in REQUIRED_FIELDS:
            raise ValueError(f"Glossary term field cannot be cleared: {key}")

        data, current_value = self._field_data(key)
        value = [] if isinstance(current_value, list) else ""
        return self._with_field(data, key, value)

    def _field_data(self, key: str) -> tuple[dict[str, Any], Any]:
        data = self.model_dump(mode="python")

        if key not in data:
            raise ValueError(f"Glossary term has no field: {key}")

        return data, data[key]

    def _with_field(
        self, data: dict[str, Any], key: str, value: Any
    ) -> "GlossaryTerm":
        data[key] = value
        return GlossaryTerm.model_validate(data)
