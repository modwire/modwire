from ..base import (
    ArchitectureMapQuery,
    BaseShapeResolver,
    ShapeViolation,
    SignatureShape,
    SymbolShapeResolverInterface,
)
from modwire.shared.config import ShapeConfig


class SignatureResolver(SymbolShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "signature"

    @property
    def title(self) -> str:
        return "Signature Shape"

    def resolve(
        self,
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for interface_result in architecture_map.code_map.interfaces().all():
            source_interface = interface_result.item
            for signature in getattr(source_interface, "signatures", ()):
                violations.extend(
                    self.signature_violations(
                        source_id=interface_result.source_id,
                        symbol_name=getattr(source_interface, "name", ""),
                        signature=signature,
                        config=config,
                    )
                )
        for type_result in architecture_map.code_map.types().all():
            source_type = type_result.item
            for signature in getattr(source_type, "signatures", ()):
                violations.extend(
                    self.signature_violations(
                        source_id=type_result.source_id,
                        symbol_name=getattr(source_type, "name", ""),
                        signature=signature,
                        config=config,
                    )
                )
        return tuple(violations)

    def signature_violations(
        self,
        *,
        source_id: str,
        symbol_name: str,
        signature: SignatureShape,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations = [
            self.limit_violation(
                source_id=source_id,
                rule_name="max_declared_args",
                actual=signature.declared_args,
                limit=config.max_declared_args,
                symbol_kind="signature",
                symbol_name=symbol_name,
            )
        ]
        if not config.allow_optional_method_args and signature.optional_args:
            violations.append(
                ShapeViolation(
                    source_id=source_id,
                    rule_name="allow_optional_method_args",
                    actual=True,
                    limit=False,
                    symbol_kind="signature",
                    symbol_name=symbol_name,
                )
            )
        return tuple(violation for violation in violations if violation is not None)
