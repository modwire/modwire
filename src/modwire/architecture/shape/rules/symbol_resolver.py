from modwire_extraction.extractors.source import SourceFile

from ..base import ShapeResolver, ShapeViolation
from ..config import ShapeConfig
from .abstract_class_resolver import AbstractClassResolver
from .callable_resolver import CallableResolver
from .class_resolver import ClassResolver
from .property_resolver import PropertyResolver
from .signature_resolver import SignatureResolver


class SymbolResolver(ShapeResolver):
    name: str = "symbol"
    title: str = "Symbol Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for resolver in (
            ClassResolver(),
            AbstractClassResolver(),
            CallableResolver(),
            SignatureResolver(),
            PropertyResolver(),
        ):
            violations.extend(resolver.resolve(source_id, source_file, config))
        return tuple(violations)


__all__ = ["SymbolResolver"]
