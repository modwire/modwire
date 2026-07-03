import abc

from ...boundaries.map import ArchitectureMap

from .catalog import ShapeResolverCatalog
from .report import ShapeReport, ShapeViolation


class ShapePipelineStepInterface(abc.ABC):
    @abc.abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> ShapeReport:
        raise NotImplementedError


class ShapePipelineStep(ShapePipelineStepInterface):
    def __init__( self, resolvers: tuple[str, ...]):
        self.catalog = ShapeResolverCatalog()
        self.resolvers = resolvers

    def run(self, architecture_map: ArchitectureMap) -> ShapeReport:
        violations: list[ShapeViolation] = []
        config = architecture_map.config.shape
        for resolver_name in self.resolvers:
            resolver = self.catalog.resolver(resolver_name)
            for source_file in architecture_map.code_map.source_files().all():
                violations.extend(
                    resolver.resolve(
                        source_file.source_id,
                        source_file.file,
                        config,
                    )
                )
        return ShapeReport(
            violations=tuple(violations),
            resolvers=self.resolvers,
        )
