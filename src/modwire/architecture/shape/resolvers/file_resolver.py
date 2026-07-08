from modwire_extraction.extractors.source import SourceFile

from ..base import ShapeResolverInterface, BaseShapeResolver, ShapeViolation
from ....shared.config.shape import ShapeConfig


class FileResolver(ShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "file"

    @property
    def title(self) -> str:
        return "File Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations = [
            self.limit_violation(
                source_id=source_id,
                rule_name="max_classes_per_file",
                actual=len(source_file.classes),
                limit=config.max_classes_per_file,
                symbol_kind="file",
            ),
            self.limit_violation(
                source_id=source_id,
                rule_name="max_interfaces_per_file",
                actual=len(source_file.interfaces),
                limit=config.max_interfaces_per_file,
                symbol_kind="file",
            ),
            self.limit_violation(
                source_id=source_id,
                rule_name="max_types_per_file",
                actual=len(source_file.types),
                limit=config.max_types_per_file,
                symbol_kind="file",
            ),
            self.limit_violation(
                source_id=source_id,
                rule_name="max_abstract_classes_per_file",
                actual=len(source_file.abstract_classes),
                limit=config.max_abstract_classes_per_file,
                symbol_kind="file",
            ),
            self.limit_violation(
                source_id=source_id,
                rule_name="max_functions_per_file",
                actual=len(source_file.functions),
                limit=config.max_functions_per_file,
                symbol_kind="file",
            ),
        ]
        return tuple(violation for violation in violations if violation is not None)
