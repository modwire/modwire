from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pydantic import Field

from modwire_extraction.code import CodeMap, QueryableCodeMap

from ..boundaries import ArchitectureMapLoader
from ..boundaries.reports import (
    ArchitectureMapReport,
    ArchitectureMapReportCollector,
    FlowReport,
    FlowReportCollector,
)
from ..config import ArchitectureConfig
from ..insight.reports import (
    InsightReport,
    InsightReportCollector,
    InsightReporterCatalog,
)
from ..shape.reports import (
    ShapeReport,
    ShapeReportCollector,
)
from ..report import ReportCategory, ReportSection


if TYPE_CHECKING:
    from ..boundaries import ArchitectureMap


class ArchitectureViolationReport(ReportSection):
    report_id: ClassVar[str] = "architecture.violations"
    report_title: ClassVar[str] = "Architecture Violations"
    report_category: ClassVar[ReportCategory] = ReportCategory.VIOLATIONS
    report_path: ClassVar[str] = "violations"
    report_order: ClassVar[int] = 20
    report_children: ClassVar = (FlowReport, ShapeReport)

    flow: FlowReport = Field(default_factory=FlowReport)
    shape: ShapeReport = Field(default_factory=ShapeReport)


class ArchitectureReport(ReportSection):
    report_id: ClassVar[str] = "architecture"
    report_title: ClassVar[str] = "Architecture Report"
    report_category: ClassVar[ReportCategory] = ReportCategory.ROOT
    report_path: ClassVar[str] = ""
    report_order: ClassVar[int] = 0
    report_children: ClassVar = (
        ArchitectureMapReport,
        ArchitectureViolationReport,
        InsightReport,
    )

    map: ArchitectureMapReport
    violations: ArchitectureViolationReport
    insights: InsightReport = Field(default_factory=InsightReport)


class ArchitectureReportRunner:
    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def run(self, code_map: CodeMap | QueryableCodeMap) -> ArchitectureReport:
        architecture_map = ArchitectureMapLoader(self.config).load(
            self.queryable_code_map(code_map)
        )
        return self.run_map(architecture_map)

    def run_map(self, architecture_map: ArchitectureMap) -> ArchitectureReport:
        flow_report = FlowReportCollector().collect_all(architecture_map)
        shape_report = ShapeReportCollector().collect(
            architecture_map,
            self.shape_resolvers(),
        )
        insight_report = InsightReportCollector().collect(
            architecture_map,
            self.insight_reporters(),
        )
        return ArchitectureReport(
            map=ArchitectureMapReportCollector().collect(architecture_map),
            violations=ArchitectureViolationReport(
                flow=flow_report,
                shape=shape_report,
            ),
            insights=insight_report,
        )

    def shape_resolvers(self) -> tuple[str, ...]:
        return ("file", "import", "symbol")

    def insight_reporters(self) -> tuple[str, ...]:
        return InsightReporterCatalog().names()

    def queryable_code_map(
        self,
        code_map: CodeMap | QueryableCodeMap,
    ) -> QueryableCodeMap:
        if isinstance(code_map, QueryableCodeMap):
            return code_map
        return QueryableCodeMap(code_map)


__all__ = [
    "ArchitectureMapReport",
    "ArchitectureReport",
    "ArchitectureReportRunner",
    "ArchitectureViolationReport",
]
