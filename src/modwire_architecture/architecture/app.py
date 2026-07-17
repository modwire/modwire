from typing import Any, Protocol

from modwire_extraction.code import QueryableCodeMap
from modwire_architecture.shared import config, report

from .contract import ArchitectureAnalysis
from .normalization import normalize_analysis

class _ArchitectureMapLoader(Protocol):
    def load(self, code_map: QueryableCodeMap) -> Any: ...


class _ArchitectureReportCollector(Protocol):
    report_type: type[report.ReportItem]

    def collect(self, architecture_map: Any) -> report.ReportNode: ...


class ArchitectureApplication:
    def __init__(
        self,
        config: config.ArchitectureConfig,
    ):
        from .composition import standard_architecture_components

        self.config = config
        self._map_loader, self._collectors = standard_architecture_components(config)

    @classmethod
    def standard(
        cls,
        config_: config.ArchitectureConfig,
    ) -> "ArchitectureApplication":
        """Build the supported architecture-reporting composition."""
        return cls(config_)

    def reports(self) -> report.ReportCatalog:
        reports = tuple(
            collector.report_type.report_metadata()
            for collector in self._collectors
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

    def report(self, code_map: QueryableCodeMap) -> tuple[report.ReportNode, ...]:
        architecture_map = self._map_loader.load(code_map)

        reports = tuple(
            collector.collect(architecture_map)
            for collector in self._collectors
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

    def analyze(self, code_map: QueryableCodeMap) -> ArchitectureAnalysis:
        """Analyze extracted facts through the supported public result contract."""
        return normalize_analysis(self.config, self.report(code_map))
