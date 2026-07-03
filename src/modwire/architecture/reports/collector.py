from typing import TYPE_CHECKING

from ..boundaries.reports import ArchitectureMapReportCollector, FlowReportCollector
from ..insight.reports import InsightReportCollector, InsightReporterCatalog
from ..shape.reports import ShapeReportCollector
from .architecture import ArchitectureReport, ArchitectureViolationReport


if TYPE_CHECKING:
    from ..boundaries import ArchitectureMap


class ArchitectureReportCollector:
    def __init__(
        self,
    ):
        self.map_collector = ArchitectureMapReportCollector()
        self.flow_collector = FlowReportCollector()
        self.shape_collector = ShapeReportCollector(
            ("file", "import", "symbol")
        )
        self.insight_collector = InsightReportCollector(
            InsightReporterCatalog().names()
        )

    def collect(self, architecture_map: ArchitectureMap) -> ArchitectureReport:
        return ArchitectureReport(
            map=self.map_collector.collect(architecture_map),
            violations=ArchitectureViolationReport(
                flow=self.flow_collector.collect(architecture_map),
                shape=self.shape_collector.collect(architecture_map),
            ),
            insights=self.insight_collector.collect(architecture_map),
        )
