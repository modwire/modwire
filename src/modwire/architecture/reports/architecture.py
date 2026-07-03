from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pydantic import Field

from modwire_extraction.code import CodeMap, QueryableCodeMap

from ..boundaries import ArchitectureMapLoader
from ..boundaries.reports import ArchitectureMapReport, FlowReport
from ..config import ArchitectureConfig
from ..insight.reports import InsightReport
from ..shape.reports import ShapeReport
from ..report import ReportCategory, ReportCollector, ReportSection


if TYPE_CHECKING:
    from ..boundaries import ArchitectureMap
    from .collector import ArchitectureReportCollector


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
    def __init__(
        self,
        config: ArchitectureConfig,
        report_collector: ReportCollector[ArchitectureReport] | None = None,
    ):
        self.config = config
        self.report_collector = report_collector or self.default_report_collector()

    def run(self, code_map: CodeMap | QueryableCodeMap) -> ArchitectureReport:
        architecture_map = ArchitectureMapLoader(self.config).load(
            self.queryable_code_map(code_map)
        )
        return self.run_map(architecture_map)

    def run_map(self, architecture_map: ArchitectureMap) -> ArchitectureReport:
        return self.report_collector.collect(architecture_map)

    def default_report_collector(self) -> ArchitectureReportCollector:
        from .collector import ArchitectureReportCollector

        return ArchitectureReportCollector()

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
