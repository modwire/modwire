import re
from typing import Any, ClassVar, List

from pydantic import AnyUrl, Field

from modwire.shared import ModwireBaseModel


class GlossaryTerm(ModwireBaseModel):
    _IDENTITY_FIELDS: ClassVar[set[str]] = {"id", "parent_id"}
    _REQUIRED_FIELDS: ClassVar[set[str]] = {*_IDENTITY_FIELDS, "term", "definition"}

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
        term_id = cls._slug(term)
        if not term_id:
            raise ValueError("Term must contain at least one letter or number.")

        return cls(
            id=term_id,
            parent_id=parent_id or term_id,
            term=term,
            definition=definition,
            aliases=cls._deduplicate(aliases),
            relations=cls._deduplicate(relations),
            sources=cls._deduplicate(sources),
        )

    def update_data(self, key: str, new_value: str) -> "GlossaryTerm":
        if key in self._IDENTITY_FIELDS:
            raise ValueError(f"Glossary term field cannot be updated: {key}")

        data, current_value = self._field_data(key)
        value = (
            self._deduplicate([*current_value, new_value])
            if isinstance(current_value, list)
            else new_value
        )
        return self._with_field(data, key, value)

    def remove_data(self, key: str) -> "GlossaryTerm":
        if key in self._REQUIRED_FIELDS:
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

    @staticmethod
    def _slug(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    @staticmethod
    def _deduplicate(values: list[Any]) -> list[Any]:
        deduplicated = []
        seen = set()

        for value in values:
            key = str(value)
            if key in seen:
                continue

            seen.add(key)
            deduplicated.append(value)

        return deduplicated
