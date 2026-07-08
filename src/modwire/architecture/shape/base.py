import abc

from modwire_extraction.extractors.source import SourceFile

from .config import ShapeConfig
from .reports import ShapeViolation


class ShapeResolverInterface(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        raise NotImplementedError


class BaseShapeResolver:
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
