from pydantic import BaseModel, ConfigDict, Field

from modwire_extraction.code import CodeMap, QueryableCodeMap

from .boundaries.map import ArchitectureMap, ArchitectureMapLoader
from .boundaries.pipeline import FlowPipelineStep, FlowReport
from .config import ArchitectureConfig
from .insight.pipeline import InsightPipelineStep, InsightReport, InsightReporterCatalog
from .shape.pipeline import ShapePipelineStep, ShapeReport


class ArchitectureGroup(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str
    source_ids: tuple[str, ...]


class ArchitectureMapReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    modules: tuple[ArchitectureGroup, ...] = ()
    layers: tuple[ArchitectureGroup, ...] = ()
    unknown_files: tuple[str, ...] = ()

    @classmethod
    def from_map(cls, architecture_map: ArchitectureMap) -> "ArchitectureMapReport":
        return cls(
            modules=tuple(
                ArchitectureGroup(name=name, source_ids=source_ids)
                for name, source_ids in sorted(architecture_map.modules.items())
            ),
            layers=tuple(
                ArchitectureGroup(name=name, source_ids=source_ids)
                for name, source_ids in sorted(architecture_map.layers.items())
            ),
            unknown_files=architecture_map.unknown_files,
        )


class ArchitectureViolationReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    flow: FlowReport = Field(default_factory=FlowReport)
    shape: ShapeReport = Field(default_factory=ShapeReport)


class ArchitectureReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

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
    "ArchitectureGroup",
    "ArchitectureMapReport",
    "ArchitectureReport",
    "ArchitectureReportRunner",
    "ArchitectureViolationReport",
]
