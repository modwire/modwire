from collections.abc import Sequence

from wireup import injectable

from ..base import (
    ArchitectureMapQuery,
    BaseShapeResolver,
    ShapeResolverInterface,
    ShapeViolation,
    SymbolShapeResolverInterface,
)
from modwire.shared.config import ShapeConfig


@injectable(qualifier="symbol", as_type=ShapeResolverInterface)
class SymbolResolver(ShapeResolverInterface, BaseShapeResolver):
    def __init__(self, resolvers: Sequence[SymbolShapeResolverInterface]):
        self.resolvers = tuple(sorted(resolvers, key=lambda resolver: resolver.name))

    @property
    def name(self) -> str:
        return "symbol"

    @property
    def title(self) -> str:
        return "Symbol Shape"

    def resolve(
        self,
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for resolver in self.resolvers:
            violations.extend(resolver.resolve(architecture_map, config))
        return tuple(violations)
