from modwire_extraction.extractors.source import (
    SourceClassMethod,
    SourceFile,
    SourceFunction,
)

from ..base import ShapeResolverInterface, BaseShapeResolver, ShapeViolation
from ....shared.config.shape import ShapeConfig


class CallableResolver(ShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "callable"

    @property
    def title(self) -> str:
        return "Callable Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for source_function in source_file.functions:
            violations.extend(
                self.callable_violations(
                    source_id=source_id,
                    symbol_kind="function",
                    symbol=source_function,
                    line_limit=config.max_function_lines,
                    allow_optional_args=config.allow_optional_function_args,
                    config=config,
                )
            )

        for source_class in source_file.classes:
            for method in source_class.methods:
                violations.extend(
                    self.callable_violations(
                        source_id=source_id,
                        symbol_kind="method",
                        symbol=method,
                        line_limit=config.max_method_lines,
                        allow_optional_args=config.allow_optional_method_args,
                        config=config,
                    )
                )

        for source_interface in source_file.interfaces:
            for method in source_interface.methods:
                violations.extend(
                    self.callable_violations(
                        source_id=source_id,
                        symbol_kind="method",
                        symbol=method,
                        line_limit=config.max_method_lines,
                        allow_optional_args=config.allow_optional_method_args,
                        config=config,
                    )
                )

        for abstract_class in source_file.abstract_classes:
            for method in (
                *abstract_class.abstract_methods,
                *abstract_class.concrete_methods,
            ):
                violations.extend(
                    self.callable_violations(
                        source_id=source_id,
                        symbol_kind="method",
                        symbol=method,
                        line_limit=config.max_method_lines,
                        allow_optional_args=config.allow_optional_method_args,
                        config=config,
                    )
                )

        return tuple(violations)

    def callable_violations(
        self,
        *,
        source_id: str,
        symbol_kind: str,
        symbol: SourceFunction | SourceClassMethod,
        line_limit: int,
        allow_optional_args: bool,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        line_rule = (
            "max_function_lines"
            if symbol_kind == "function"
            else "max_method_lines"
        )
        violations = [
            self.limit_violation(
                source_id=source_id,
                rule_name=line_rule,
                actual=symbol.line_count,
                limit=line_limit,
                symbol_kind=symbol_kind,
                symbol_name=symbol.name,
            ),
            self.limit_violation(
                source_id=source_id,
                rule_name="max_declared_args",
                actual=symbol.declared_args,
                limit=config.max_declared_args,
                symbol_kind=symbol_kind,
                symbol_name=symbol.name,
            ),
        ]
        if not allow_optional_args and symbol.optional_args:
            violations.append(
                ShapeViolation(
                    source_id=source_id,
                    rule_name=(
                        "allow_optional_function_args"
                        if symbol_kind == "function"
                        else "allow_optional_method_args"
                    ),
                    actual=True,
                    limit=False,
                    symbol_kind=symbol_kind,
                    symbol_name=symbol.name,
                )
            )
        return tuple(violation for violation in violations if violation is not None)
