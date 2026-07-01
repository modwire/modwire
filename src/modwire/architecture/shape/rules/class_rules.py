class ClassLimitRule:
    def _class_violations(
        self,
        source_id: str,
        symbol_kind: str,
        source_class: SourceClass | SourceInterface | SourceType,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations = [
            _limit_violation(
                source_id,
                "max_class_lines",
                source_class.line_count,
                config.max_class_lines,
                symbol_kind,
                source_class.name,
            )
        ]
        if hasattr(source_class, "methods"):
            violations.append(
                _limit_violation(
                    source_id,
                    "max_methods_per_class",
                    len(source_class.methods),
                    config.max_methods_per_class,
                    symbol_kind,
                    source_class.name,
                )
            )
        return tuple(violation for violation in violations if violation is not None)
