from wireup import injectable

from modwire.shared import ModwireBaseApplication, config

from .boundaries.analyzer import BoundariesFlowAnalyzer
from .map.loader import ArchitectureMapLoader
from .shape.resolvers.catalog import ShapeResolverCatalog


@injectable(lifetime="transient")
class ArchitectureApplication(ModwireBaseApplication):
    def __init__(
        self,
        config: config.ArchitectureConfig,
        map_loader: ArchitectureMapLoader,
        flow_analyzer: BoundariesFlowAnalyzer,
        shape_catalog: ShapeResolverCatalog,
    ):
        self.config = config
        self.map_loader = map_loader
        self.flow_analyzer = flow_analyzer
        self.shape_catalog = shape_catalog

    def run(self):
        pass
