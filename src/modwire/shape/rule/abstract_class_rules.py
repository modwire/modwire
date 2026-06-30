class AbstractClassRules:
    def _abstract_class_violations(
        self,
        source_id: str,
        abstract_class: SourceAbstractClass,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        methods = (*abstract_class.abstract_methods, *abstract_class.concrete_methods)
        violations = [
            _limit_violation(
                source_id,
                "max_class_lines",
                abstract_class.line_count,
                config.max_class_lines,
                "abstract_class",
                abstract_class.name,
            ),
            _limit_violation(
                source_id,
                "max_methods_per_class",
                len(methods),
                config.max_methods_per_class,
                "abstract_class",
                abstract_class.name,
            ),
        ]
        for method in methods:
            violations.extend(_callable_violations(source_id, "method", method, config))
        violations.extend(
            _property_violations(
                source_id,
                "abstract_class_property",
                abstract_class.properties,
                config,
            )
        )
        return tuple(violation for violation in violations if violation is not None)
