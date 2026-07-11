import abc
from collections.abc import Sequence
from typing import Protocol

from modwire_extraction.code import QueryableCodeMap
from modwire.shared import ModwireModel
from modwire.shared.config import ShapeConfig


class ArchitectureMapQuery(Protocol):
    code_map: QueryableCodeMap


class NamedLineShape(Protocol):
    name: str
    line_count: int


class CallableShape(NamedLineShape, Protocol):
    declared_args: int
    optional_args: bool


class AbstractClassShape(NamedLineShape, Protocol):
    abstract_methods: Sequence[CallableShape]
    concrete_methods: Sequence[CallableShape]


class PropertyShape(Protocol):
    name: str
    is_optional: bool


class SignatureShape(Protocol):
    declared_args: int
    optional_args: bool


class ShapeViolation(ModwireModel):
    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    symbol_kind: str = ""
    symbol_name: str = ""


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
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        raise NotImplementedError


class SymbolShapeResolverInterface(ShapeResolverInterface):
    pass


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
