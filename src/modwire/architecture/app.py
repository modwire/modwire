from wireup import injectable

from modwire.shared import ConfigResolver, ModwireApplication

from .boundaries.analyzer import BoundariesFlowAnalyzer
from .map.loader import ArchitectureMapLoader
from .shape.resolvers.catalog import ShapeResolverCatalog


@injectable(lifetime="transient")
class ArchitectureApplication(ModwireApplication):
    def __init__(
        self,
        config_resolver: ConfigResolver,
        map_loader: ArchitectureMapLoader,
        flow_analyzer: BoundariesFlowAnalyzer,
        shape_catalog: ShapeResolverCatalog,
    ):
        self.config = config_resolver.architecture()
        self.map_loader = map_loader
        self.flow_analyzer = flow_analyzer
        self.shape_catalog = shape_catalog

    def run(self):
        pass
