from typing import Annotated

from wireup import Inject, injectable

from modwire.shared import config

from .boundaries import FlowReportCollector
from .map import ArchitectureMapLoader, MapReportCollector
from .insights import InsightReportCollector
from .shape import ShapeReportCollector


@injectable(lifetime="transient")
class ArchitectureApplication:
    def __init__(
        self,
        config: Annotated[config.ArchitectureConfig, Inject(config="architecture")],
        map_loader: ArchitectureMapLoader,
        map_report_collector: MapReportCollector,
        flow_report_collector: FlowReportCollector,
        insight_report_collector: InsightReportCollector,
        shape_report_collector: ShapeReportCollector
    ):
        self.config = config
        self.map_loader = map_loader
        self.map_report_collector = map_report_collector
        self.flow_report_collector = flow_report_collector
        self.insight_report_collector = insight_report_collector
        self.shape_report_collector = shape_report_collector
