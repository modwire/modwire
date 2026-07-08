from modwire.shared import ModwireApplication

from .boundaries.analyzer import BoundariesFlowAnalyzer
from .config import ArchitectureConfig
from .map.loader import ArchitectureMapLoader
from .shape.resolvers.catalog import ShapeResolverCatalog


class ArchitectureApplication(ModwireApplication):
    def __init__(
        self,
        config: ArchitectureConfig,
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
