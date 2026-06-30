class CallableRules:
    def _callable_violations(
        self,
        source_id: str,
        symbol_kind: str,
        callable_symbol: SourceFunction | SourceClassMethod,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        line_rule = "max_function_lines" if symbol_kind == "function" else "max_method_lines"
        line_limit = (
            config.max_function_lines
            if symbol_kind == "function"
            else config.max_method_lines
        )
        allow_optional = (
            config.allow_optional_function_args
            if symbol_kind == "function"
            else config.allow_optional_method_args
        )
        violations = [
            _limit_violation(
                source_id,
                "max_declared_args",
                callable_symbol.declared_args,
                config.max_declared_args,
                symbol_kind,
                callable_symbol.name,
            ),
            _limit_violation(
                source_id,
                line_rule,
                callable_symbol.line_count,
                line_limit,
                symbol_kind,
                callable_symbol.name,
            ),
        ]
        if not allow_optional and callable_symbol.optional_args > 0:
            violations.append(
                ShapeViolation(
                    source_id,
                    f"allow_optional_{symbol_kind}_args",
                    True,
                    False,
                    symbol_kind,
                    callable_symbol.name,
                )
            )
        return tuple(violation for violation in violations if violation is not None)