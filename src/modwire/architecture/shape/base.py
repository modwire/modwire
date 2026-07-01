import abc

from modwire_extraction.extractors.source import SourceFile
from pydantic import BaseModel, ConfigDict

from .config import ShapeConfig


class ShapeViolation(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    symbol_kind: str = ""
    symbol_name: str = ""


class ShapeResolver(BaseModel, abc.ABC):
    name: str
    title: str

    @abc.abstractmethod
    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        raise NotImplementedError

    def limit_violation(
        self,
        *,
        source_id: str,
        rule_name: str,
        actual: int,
        limit: int,
        symbol_kind: str = "",
        symbol_name: str = "",
    ) -> ShapeViolation | None:
        if limit < 0 or actual <= limit:
            return None
        return ShapeViolation(
            source_id=source_id,
            rule_name=rule_name,
            actual=actual,
            limit=limit,
            symbol_kind=symbol_kind,
            symbol_name=symbol_name,
        )
