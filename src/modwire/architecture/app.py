from pathlib import Path
from typing import Annotated

from wireup import Inject, injectable

from modwire.shared import config, report
from modwire.code import QueryableCodeMapReader

from .boundaries import FlowReportCollector
from .insights import InsightReportCollector
from .map import ArchitectureMapLoader, MapReportCollector
from .shape import ShapeReportCollector


@injectable(lifetime="transient")
class ArchitectureApplication:
    def __init__(
        self,
        config: Annotated[config.ArchitectureConfig, Inject(config="architecture")],
        code_map_reader: QueryableCodeMapReader,
        map_loader: ArchitectureMapLoader,
        map_report_collector: MapReportCollector,
        flow_report_collector: FlowReportCollector,
        insight_report_collector: InsightReportCollector,
        shape_report_collector: ShapeReportCollector,
    ):
        self.config = config
        self.code_map_reader = code_map_reader
        self.map_loader = map_loader
        self.map_report_collector = map_report_collector
        self.flow_report_collector = flow_report_collector
        self.insight_report_collector = insight_report_collector
        self.shape_report_collector = shape_report_collector

    def reports(self) -> report.ReportCatalog:
        reports = tuple(
            collector.report_type.report_metadata()
            for collector in (
                self.map_report_collector,
                self.flow_report_collector,
                self.shape_report_collector,
                self.insight_report_collector,
            )
        )
        return report.ReportCatalog(
            reports=tuple(
                sorted(
                    reports,
                    key=lambda report_metadata: (
                        report_metadata.order,
                        report_metadata.id,
                    ),
                )
            )
        )

    def report(self, root: Path, language: str) -> tuple[report.ReportNode, ...]:
        code_map = self.code_map_reader.read(root, language)
        architecture_map = self.map_loader.load(code_map)

        reports = (
            self.map_report_collector.collect(architecture_map),
            self.flow_report_collector.collect(architecture_map),
            self.insight_report_collector.collect(architecture_map),
            self.shape_report_collector.collect(architecture_map),
        )
        return tuple(
            sorted(
                reports,
                key=lambda report_node: (
                    report_node.metadata.order,
                    report_node.metadata.id,
                ),
            )
        )
