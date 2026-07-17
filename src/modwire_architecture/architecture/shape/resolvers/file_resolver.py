from ..base import (
    ArchitectureMapQuery,
    BaseShapeResolver,
    ShapeResolverInterface,
    ShapeViolation,
)
from modwire_architecture.shared.config import ShapeConfig


class FileResolver(ShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "file"

    @property
    def title(self) -> str:
        return "File Shape"

    def resolve(
        self,
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation | None] = []
        code_map = architecture_map.code_map

        for source_id in code_map.source_ids():
            violations.extend(
                [
                    self.limit_violation(
                        source_id=source_id,
                        rule_name="max_classes_per_file",
                        actual=code_map.classes()
                        .where_equal(lambda result: result.source_id, source_id)
                        .count(),
                        limit=config.max_classes_per_file,
                        symbol_kind="file",
                    ),
                    self.limit_violation(
                        source_id=source_id,
                        rule_name="max_interfaces_per_file",
                        actual=code_map.interfaces()
                        .where_equal(lambda result: result.source_id, source_id)
                        .count(),
                        limit=config.max_interfaces_per_file,
                        symbol_kind="file",
                    ),
                    self.limit_violation(
                        source_id=source_id,
                        rule_name="max_types_per_file",
                        actual=code_map.types()
                        .where_equal(lambda result: result.source_id, source_id)
                        .count(),
                        limit=config.max_types_per_file,
                        symbol_kind="file",
                    ),
                    self.limit_violation(
                        source_id=source_id,
                        rule_name="max_abstract_classes_per_file",
                        actual=code_map.abstract_classes()
                        .where_equal(lambda result: result.source_id, source_id)
                        .count(),
                        limit=config.max_abstract_classes_per_file,
                        symbol_kind="file",
                    ),
                    self.limit_violation(
                        source_id=source_id,
                        rule_name="max_functions_per_file",
                        actual=code_map.functions()
                        .where_equal(lambda result: result.source_id, source_id)
                        .count(),
                        limit=config.max_functions_per_file,
                        symbol_kind="file",
                    ),
                ]
            )
        return tuple(violation for violation in violations if violation is not None)
