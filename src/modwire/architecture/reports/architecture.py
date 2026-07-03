from pydantic import Field

from modwire_extraction.code import CodeMap, QueryableCodeMap

from modwire.shared import ModwireBaseModel

from ..boundaries.map import ArchitectureMap, ArchitectureMapLoader
from ..boundaries.pipeline.step import FlowPipelineStep
from ..boundaries.reports import ArchitectureMapReport, FlowReport
from ..config import ArchitectureConfig
from ..insight.pipeline.step import (
    InsightPipelineStep,
    InsightReport,
    InsightReporterCatalog,
)
from ..shape.pipeline.report import ShapeReport
from ..shape.pipeline.step import ShapePipelineStep


class ArchitectureViolationReport(ModwireBaseModel):
    flow: FlowReport = Field(default_factory=FlowReport)
    shape: ShapeReport = Field(default_factory=ShapeReport)


class ArchitectureReport(ModwireBaseModel):
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
        flow_report = FlowPipelineStep().run_all(architecture_map)
        shape_report = ShapePipelineStep(self.shape_resolvers()).run(architecture_map)
        insight_report = InsightPipelineStep(self.insight_reporters()).run(
            architecture_map
        )
        return ArchitectureReport(
            map=ArchitectureMapReport.from_map(architecture_map),
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
