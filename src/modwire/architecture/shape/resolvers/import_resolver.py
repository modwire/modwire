from modwire_extraction.extractors.source import SourceFile

from ..base import ShapeResolverInterface, BaseShapeResolver, ShapeViolation
from ..config import ShapeConfig


class ImportResolver(ShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "import"

    @property
    def title(self) -> str:
        return "Import Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        allowed_crossing_types = set(config.allowed_import_crossing_types)

        for source_import in source_file.imports:
            if not config.allow_import_aliases and source_import.is_aliased:
                violations.append(
                    ShapeViolation(
                        source_id=source_id,
                        rule_name="allow_import_aliases",
                        actual=False,
                        limit=False,
                        symbol_kind="import",
                        symbol_name=source_import.normalized_path,
                    )
                )
            if source_import.crossing_type not in allowed_crossing_types:
                violations.append(
                    ShapeViolation(
                        source_id=source_id,
                        rule_name="allowed_import_crossing_types",
                        actual=source_import.crossing_type,
                        limit=",".join(config.allowed_import_crossing_types),
                        symbol_kind="import",
                        symbol_name=source_import.normalized_path,
                    )
                )
            if config.require_joined_imports and not source_import.uses_joined_import:
                violations.append(
                    ShapeViolation(
                        source_id=source_id,
                        rule_name="require_joined_imports",
                        actual=True,
                        limit=True,
                        symbol_kind="import",
                        symbol_name=source_import.join_key,
                    )
                )

        return tuple(violations)
