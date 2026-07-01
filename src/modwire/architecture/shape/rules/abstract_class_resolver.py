from modwire_extraction.extractors.source import SourceAbstractClass, SourceFile

from ..base import ShapeResolver, ShapeViolation
from ..config import ShapeConfig


class AbstractClassResolver(ShapeResolver):
    name: str = "abstract-class"
    title: str = "Abstract Class Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for abstract_class in source_file.abstract_classes:
            violations.extend(
                self.abstract_class_violations(
                    source_id=source_id,
                    abstract_class=abstract_class,
                    config=config,
                )
            )
        return tuple(violations)

    def abstract_class_violations(
        self,
        *,
        source_id: str,
        abstract_class: SourceAbstractClass,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        method_count = (
            len(abstract_class.abstract_methods)
            + len(abstract_class.concrete_methods)
        )
        violations = [
            self.limit_violation(
                source_id=source_id,
                rule_name="max_class_lines",
                actual=abstract_class.line_count,
                limit=config.max_class_lines,
                symbol_kind="abstract_class",
                symbol_name=abstract_class.name,
            ),
            self.limit_violation(
                source_id=source_id,
                rule_name="max_methods_per_class",
                actual=method_count,
                limit=config.max_methods_per_class,
                symbol_kind="abstract_class",
                symbol_name=abstract_class.name,
            ),
        ]
        return tuple(violation for violation in violations if violation is not None)


__all__ = ["AbstractClassResolver"]
