from ..base import RuleResolver, ShapeViolation
from ..config import ShapeConfig


class SignatureResolver(RuleResolver):
    def resolve(self, source_id: str, config: ShapeConfig) -> tuple[ShapeViolation, ...]:
        return ()
