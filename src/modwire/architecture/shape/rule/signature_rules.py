def _signature_violations(
    source_id: str,
    signature: SourceSignature,
    config: ShapeConfig,
) -> tuple[ShapeViolation, ...]:
    violations = [
        _limit_violation(
            source_id,
            "max_declared_args",
            signature.declared_args,
            config.max_declared_args,
            "signature",
            signature.kind,
        ),
        _limit_violation(
            source_id,
            "max_method_lines",
            signature.line_count,
            config.max_method_lines,
            "signature",
            signature.kind,
        ),
    ]
    if not config.allow_optional_method_args and signature.optional_args > 0:
        violations.append(
            ShapeViolation(
                source_id,
                "allow_optional_method_args",
                True,
                False,
                "signature",
                signature.kind,
            )
        )
    return tuple(violation for violation in violations if violation is not None)
