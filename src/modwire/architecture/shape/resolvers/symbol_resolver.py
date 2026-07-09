from collections.abc import Sequence

from modwire_extraction.extractors.source import SourceFile
from wireup import injectable

from ..base import (
    BaseShapeResolver,
    ShapeResolverInterface,
    ShapeViolation,
    SymbolShapeResolverInterface,
)
from ....shared.config.shape import ShapeConfig


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
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        violations: list[ShapeViolation] = []
        for resolver in self.resolvers:
            violations.extend(resolver.resolve(source_id, source_file, config))
        return tuple(violations)
