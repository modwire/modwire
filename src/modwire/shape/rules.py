from __future__ import annotations

from typing import Protocol

from ..definitions import (
    SourceAbstractClass,
    SourceClass,
    SourceClassMethod,
    SourceClassProperty,
    SourceFile,
    SourceFunction,
    SourceInterface,
    SourceSignature,
    SourceType,
)
from .config import ShapeConfig
from .violations import ShapeViolation


class ShapeRule(Protocol):
    def evaluate(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        ...


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


def _class_violations(
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


def _abstract_class_violations(
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


def _callable_violations(
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


def _limit_violation(
    source_id: str,
    rule_name: str,
    actual: int,
    limit: int,
    symbol_kind: str,
    symbol_name: str = "",
) -> ShapeViolation | None:
    if limit < 0 or actual <= limit:
        return None
    return ShapeViolation(source_id, rule_name, actual, limit, symbol_kind, symbol_name)


DEFAULT_SHAPE_RULES: tuple[ShapeRule, ...] = (
    FileCountRule(),
    SymbolShapeRule(),
    ImportShapeRule(),
)


__all__ = [
    "DEFAULT_SHAPE_RULES",
    "FileCountRule",
    "ImportShapeRule",
    "ShapeRule",
    "SymbolShapeRule",
]
