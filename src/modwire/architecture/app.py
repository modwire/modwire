from pathlib import Path

from modwire.shared import config, report
from modwire.code import QueryableCodeMapReader

from .boundaries.analyzer import BoundariesFlowAnalyzer
from .boundaries.analyzers.backward import BackwardFlowAnalyzer
from .boundaries.analyzers.no_cycles import NoCyclesFlowAnalyzer
from .boundaries.analyzers.no_reentry import NoReentryFlowAnalyzer
from .boundaries.collector import FlowReportCollector
from .insights.collector import InsightReportCollector
from .insights.reporters.callables import CallablesReporter
from .insights.reporters.clusters import ClustersReporter
from .insights.reporters.coherence import CoherenceReporter
from .insights.reporters.exports import ExportsReporter
from .insights.reporters.hotspots import HotspotsReporter
from .map import ArchitectureMapLoader, MapReportCollector
from .shape.collector import ShapeReportCollector
from .shape.resolvers.abstract_class_resolver import AbstractClassResolver
from .shape.resolvers.callable_resolver import CallableResolver
from .shape.resolvers.class_resolver import ClassResolver
from .shape.resolvers.file_resolver import FileResolver
from .shape.resolvers.import_resolver import ImportResolver
from .shape.resolvers.property_resolver import PropertyResolver
from .shape.resolvers.signature_resolver import SignatureResolver
from .shape.resolvers.symbol_resolver import SymbolResolver


class ArchitectureApplication:
    def __init__(
        self,
        config: config.ArchitectureConfig,
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

    @classmethod
    def standard(
        cls,
        config_: config.ArchitectureConfig | None = None,
        *,
        code_map_reader: QueryableCodeMapReader | None = None,
    ) -> "ArchitectureApplication":
        """Build the supported architecture-reporting composition."""

        architecture_config = config_ or config.ArchitectureConfig()
        map_loader = ArchitectureMapLoader(architecture_config)
        flow_analyzer = BoundariesFlowAnalyzer(
            architecture_config,
            (
                BackwardFlowAnalyzer(),
                NoCyclesFlowAnalyzer(),
                NoReentryFlowAnalyzer(),
            ),
        )
        symbol_resolver = SymbolResolver(
            (
                AbstractClassResolver(),
                CallableResolver(),
                ClassResolver(),
                PropertyResolver(),
                SignatureResolver(),
            )
        )
        return cls(
            config=architecture_config,
            code_map_reader=code_map_reader or QueryableCodeMapReader(),
            map_loader=map_loader,
            map_report_collector=MapReportCollector(),
            flow_report_collector=FlowReportCollector(flow_analyzer),
            insight_report_collector=InsightReportCollector(
                (
                    CallablesReporter(),
                    ClustersReporter(),
                    CoherenceReporter(),
                    ExportsReporter(),
                    HotspotsReporter(),
                )
            ),
            shape_report_collector=ShapeReportCollector(
                architecture_config,
                (FileResolver(), ImportResolver(), symbol_resolver),
            ),
        )

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
