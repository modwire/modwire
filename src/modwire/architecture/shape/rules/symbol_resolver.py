from ..base import RuleResolver, ShapeViolation
from ..config import ShapeConfig


class SymbolResolver(RuleResolver):
    def resolve(self, source_id: str, config: ShapeConfig) -> tuple[ShapeViolation, ...]:
        return ()
