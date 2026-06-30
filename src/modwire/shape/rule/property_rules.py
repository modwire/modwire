def _property_violations(
    source_id: str,
    symbol_kind: str,
    properties: list[SourceClassProperty],
    config: ShapeConfig,
) -> tuple[ShapeViolation, ...]:
    if config.allow_optional_class_properties:
        return ()
    return tuple(
        ShapeViolation(
            source_id,
            "allow_optional_class_properties",
            True,
            False,
            symbol_kind,
            property.name,
        )
        for property in properties
        if property.is_optional
    )
