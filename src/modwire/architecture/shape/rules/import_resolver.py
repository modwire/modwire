from ..base import ShapeResolver, ShapeViolation
from ..config import ShapeConfig


class ImportResolver(ShapeResolver):
    def resolve(self, source_id: str, config: ShapeConfig) -> tuple[ShapeViolation, ...]:
        return ()
