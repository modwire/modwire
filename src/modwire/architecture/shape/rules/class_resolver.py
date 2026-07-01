from collections.abc import Sized

from modwire_extraction.extractors.source import (
    SourceClass,
    SourceFile,
    SourceInterface,
    SourceType,
)

from ..base import ShapeResolver, ShapeViolation
from ..config import ShapeConfig


class ClassResolver(ShapeResolver):
    name: str = "class"
    title: str = "Class Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for source_class in source_file.classes:
            violations.extend(
                self.class_violations(
                    source_id=source_id,
                    symbol_kind="class",
                    symbol=source_class,
                    config=config,
                )
            )
        for source_interface in source_file.interfaces:
            violations.extend(
                self.class_violations(
                    source_id=source_id,
                    symbol_kind="interface",
                    symbol=source_interface,
                    config=config,
                )
            )
        for source_type in source_file.types:
            violations.extend(
                self.class_violations(
                    source_id=source_id,
                    symbol_kind="type",
                    symbol=source_type,
                    config=config,
                )
            )
        return tuple(violations)

    def class_violations(
        self,
        *,
        source_id: str,
        symbol_kind: str,
        symbol: SourceClass | SourceInterface | SourceType,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations = [
            self.limit_violation(
                source_id=source_id,
                rule_name="max_class_lines",
                actual=symbol.line_count,
                limit=config.max_class_lines,
                symbol_kind=symbol_kind,
                symbol_name=symbol.name,
            )
        ]

        methods = getattr(symbol, "methods", None)
        if isinstance(methods, Sized):
            violations.append(
                self.limit_violation(
                    source_id=source_id,
                    rule_name="max_methods_per_class",
                    actual=len(methods),
                    limit=config.max_methods_per_class,
                    symbol_kind=symbol_kind,
                    symbol_name=symbol.name,
                )
            )

        return tuple(violation for violation in violations if violation is not None)


__all__ = ["ClassResolver"]
