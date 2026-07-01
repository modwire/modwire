from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field

from ..boundaries.map import ArchitectureMap
from .base import InsightReporter
from .reports.callables import CallableReport, CallableReportEntry, CallablesReporter
from .reports.clusters import ArchitectureCluster, ClustersReport, ClustersReporter
from .reports.coherence import CoherenceReporter, CoherenceSummary
from .reports.exports import ExportsReporter, UnusedExport, UnusedExportInsight
from .reports.hotspots import DependencyHotspot, HotspotsReport, HotspotsReporter


DEFAULT_REPORTERS = (
    "clusters",
    "hotspots",
    "coherence",
    "callables",
    "unused-exports",
)


class InsightReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    clusters: tuple[ArchitectureCluster, ...] = ()
    hotspots: tuple[DependencyHotspot, ...] = ()
    coherence: CoherenceSummary = Field(default_factory=CoherenceSummary)
    callables: tuple[CallableReportEntry, ...] = ()
    unused_exports: tuple[UnusedExport, ...] = ()
    reporters: tuple[str, ...] = ()


class InsightPipelineStepInterface(ABC):
    @abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> InsightReport:
        raise NotImplementedError


class InsightReporterCatalog:
    def __init__(self):
        self._reporters = {
            reporter.name: reporter
            for reporter in (
                ClustersReporter(),
                HotspotsReporter(),
                CoherenceReporter(),
                CallablesReporter(),
                ExportsReporter(),
            )
        }

    def reporter(self, name: str) -> InsightReporter:
        try:
            return self._reporters[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._reporters))
            raise ValueError(
                f"Unknown insight reporter {name!r}. Known reporters: {known}"
            ) from exc


class InsightPipelineStep(InsightPipelineStepInterface):
    def __init__(
        self,
        catalog: InsightReporterCatalog | None = None,
        reporters: tuple[str, ...] = DEFAULT_REPORTERS,
    ):
        self.catalog = catalog or InsightReporterCatalog()
        self.reporters = reporters

    def run(self, architecture_map: ArchitectureMap) -> InsightReport:
        report_payload: dict[str, object] = {"reporters": self.reporters}
        for reporter_name in self.reporters:
            reporter = self.catalog.reporter(reporter_name)
            collected = reporter.collect(architecture_map)
            report_payload.update(self.payload_for(collected))
        return InsightReport.model_validate(report_payload)

    def payload_for(self, collected: BaseModel) -> dict[str, object]:
        if isinstance(collected, ClustersReport):
            return {"clusters": collected.clusters}
        if isinstance(collected, HotspotsReport):
            return {"hotspots": collected.hotspots}
        if isinstance(collected, CoherenceSummary):
            return {"coherence": collected}
        if isinstance(collected, CallableReport):
            return {"callables": collected.entries}
        if isinstance(collected, UnusedExportInsight):
            return {"unused_exports": collected.unused_exports}
        raise TypeError(f"Unsupported insight report payload: {type(collected).__name__}")


__all__ = [
    "DEFAULT_REPORTERS",
    "InsightPipelineStep",
    "InsightPipelineStepInterface",
    "InsightReport",
    "InsightReporterCatalog",
]
