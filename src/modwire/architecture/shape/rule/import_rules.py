class ImportShapeRule:
    def evaluate(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations = []
        for source_import in source_file.imports:
            if not config.allow_import_aliases and source_import.is_aliased:
                violations.append(
                    ShapeViolation(
                        source_id,
                        "allow_import_aliases",
                        True,
                        False,
                        "import",
                        source_import.normalized_path,
                    )
                )
            if source_import.crossing_type not in config.allowed_import_crossing_types:
                violations.append(
                    ShapeViolation(
                        source_id,
                        "allowed_import_crossing_types",
                        source_import.crossing_type,
                        ",".join(config.allowed_import_crossing_types),
                        "import",
                        source_import.normalized_path,
                    )
                )
            if (
                config.require_joined_imports
                and source_import.join_key
                and not source_import.uses_joined_import
            ):
                violations.append(
                    ShapeViolation(
                        source_id,
                        "require_joined_imports",
                        False,
                        True,
                        "import",
                        source_import.join_key,
                    )
                )
        return tuple(violations)