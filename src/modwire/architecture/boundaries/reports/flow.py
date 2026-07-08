from typing import TYPE_CHECKING, ClassVar

from ...base import ReportCategory, ReportItem
from ..base import FlowViolation
from ..flow import BoundariesFlowAnalyzer


if TYPE_CHECKING:
    from ...map import ArchitectureMap


class FlowReport(ReportItem):
    report_id: ClassVar[str] = "architecture.violations.flow"
    report_title: ClassVar[str] = "Dependency Flow"
    report_category: ClassVar[ReportCategory] = ReportCategory.FLOW
    report_path: ClassVar[str] = "violations.flow"
    report_order: ClassVar[int] = 10

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowReportCollector:
    def __init__(self, flow_analyzer: BoundariesFlowAnalyzer):
        self.flow_analyzer = flow_analyzer

    def collect(self, architecture_map: "ArchitectureMap") -> FlowReport:
        return FlowReport(
            violations=self.flow_analyzer.analyze(architecture_map),
            analyzers=self.flow_analyzer.analyzer_names(),
        )
