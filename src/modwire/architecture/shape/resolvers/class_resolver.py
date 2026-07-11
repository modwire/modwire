from collections.abc import Sized

from ..base import (
    ArchitectureMapQuery,
    BaseShapeResolver,
    NamedLineShape,
    ShapeViolation,
    SymbolShapeResolverInterface,
)
from modwire.shared.config import ShapeConfig


class ClassResolver(SymbolShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "class"

    @property
    def title(self) -> str:
        return "Class Shape"

    def resolve(
        self,
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for class_result in architecture_map.code_map.classes().all():
            violations.extend(
                self.class_violations(
                    source_id=class_result.source_id,
                    symbol_kind="class",
                    symbol=class_result.item,
                    config=config,
                )
            )
        for interface_result in architecture_map.code_map.interfaces().all():
            violations.extend(
                self.class_violations(
                    source_id=interface_result.source_id,
                    symbol_kind="interface",
                    symbol=interface_result.item,
                    config=config,
                )
            )
        for type_result in architecture_map.code_map.types().all():
            violations.extend(
                self.class_violations(
                    source_id=type_result.source_id,
                    symbol_kind="type",
                    symbol=type_result.item,
                    config=config,
                )
            )
        return tuple(violations)

    def class_violations(
        self,
        *,
        source_id: str,
        symbol_kind: str,
        symbol: NamedLineShape,
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
