from typing import Annotated

from wireup import Inject, injectable

from modwire.shared import config

from .boundaries.analyzer import BoundariesFlowAnalyzer
from .map.loader import ArchitectureMapLoader
from .shape.resolvers.catalog import ShapeResolverCatalog


@injectable(lifetime="transient")
class ArchitectureApplication:
    def __init__(
        self,
        config: Annotated[config.ArchitectureConfig, Inject(config="architecture")],
        map_loader: ArchitectureMapLoader,
        flow_analyzer: BoundariesFlowAnalyzer,
        shape_catalog: ShapeResolverCatalog,
    ):
        self.config = config
        self.map_loader = map_loader
        self.flow_analyzer = flow_analyzer
        self.shape_catalog = shape_catalog
