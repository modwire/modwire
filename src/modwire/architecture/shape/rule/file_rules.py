class FileCountRule:
    def evaluate(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        return tuple(
            violation
            for violation in (
                _limit_violation(
                    source_id,
                    "max_classes_per_file",
                    len(source_file.classes),
                    config.max_classes_per_file,
                    "file",
                ),
                _limit_violation(
                    source_id,
                    "max_interfaces_per_file",
                    len(source_file.interfaces),
                    config.max_interfaces_per_file,
                    "file",
                ),
                _limit_violation(
                    source_id,
                    "max_types_per_file",
                    len(source_file.types),
                    config.max_types_per_file,
                    "file",
                ),
                _limit_violation(
                    source_id,
                    "max_abstract_classes_per_file",
                    len(source_file.abstract_classes),
                    config.max_abstract_classes_per_file,
                    "file",
                ),
                _limit_violation(
                    source_id,
                    "max_functions_per_file",
                    len(source_file.functions),
                    config.max_functions_per_file,
                    "file",
                ),
            )
            if violation is not None
        )
