class SymbolShapeRule:
    def evaluate(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for function in source_file.functions:
            violations.extend(_callable_violations(source_id, "function", function, config))

        for source_class in source_file.classes:
            violations.extend(_class_violations(source_id, "class", source_class, config))
            for method in source_class.methods:
                violations.extend(_callable_violations(source_id, "method", method, config))
            violations.extend(
                _property_violations(
                    source_id,
                    "class_property",
                    source_class.properties,
                    config,
                )
            )

        for interface in source_file.interfaces:
            violations.extend(_class_violations(source_id, "interface", interface, config))
            for method in interface.methods:
                violations.extend(_callable_violations(source_id, "method", method, config))
            for signature in interface.signatures:
                violations.extend(_signature_violations(source_id, signature, config))
            violations.extend(
                _property_violations(
                    source_id,
                    "interface_property",
                    interface.properties,
                    config,
                )
            )

        for source_type in source_file.types:
            violations.extend(_class_violations(source_id, "type", source_type, config))
            for signature in source_type.signatures:
                violations.extend(_signature_violations(source_id, signature, config))
            violations.extend(
                _property_violations(
                    source_id,
                    "type_property",
                    source_type.properties,
                    config,
                )
            )

        for abstract_class in source_file.abstract_classes:
            violations.extend(
                _abstract_class_violations(source_id, abstract_class, config)
            )
        return tuple(violations)
