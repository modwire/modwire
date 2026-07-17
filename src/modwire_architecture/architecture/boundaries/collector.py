from modwire_architecture.shared import report

from ..map.base import ArchitectureMap
from .base import FlowViolation
from .analyzer import BoundariesFlowAnalyzer


class FlowReport(report.ReportItem):
    report_id: str = "architecture.violations.flow"
    report_title: str = "Dependency Flow"
    report_description: str = (
        "Reports dependency-flow violations such as backward dependencies, "
        "cycles, and forbidden re-entry between configured architecture realms."
    )
    report_path: str = "violations.flow"
    report_order: int = 10

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowReportCollector(report.ReportCollector[FlowReport]):
    report_type: type[FlowReport] = FlowReport

    def __init__(self, flow_analyzer: BoundariesFlowAnalyzer):
        self.flow_analyzer = flow_analyzer

    def collect(self, architecture_map: ArchitectureMap) -> FlowReport:
        return self.report_type(
            violations=self.flow_analyzer.analyze(architecture_map),
            analyzers=self.flow_analyzer.analyzer_names(),
        )
