from modwire_extraction.extractors.source import SourceFile, SourceSignature

from ..base import ShapeResolver, ShapeViolation
from ..config import ShapeConfig


class SignatureResolver(ShapeResolver):
    name: str = "signature"
    title: str = "Signature Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for source_interface in source_file.interfaces:
            for signature in source_interface.signatures:
                violations.extend(
                    self.signature_violations(
                        source_id=source_id,
                        symbol_name=source_interface.name,
                        signature=signature,
                        config=config,
                    )
                )
        for source_type in source_file.types:
            for signature in source_type.signatures:
                violations.extend(
                    self.signature_violations(
                        source_id=source_id,
                        symbol_name=source_type.name,
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
        signature: SourceSignature,
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
        if (
            not config.allow_optional_method_args
            and signature.optional_args
        ):
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


__all__ = ["SignatureResolver"]
