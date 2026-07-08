from pydantic import BaseModel, Field
from wireup import injectable

from ...map.map import ArchitectureMap
from ...base import ReportCategory, ReportItem, ReportSection
from .base import InsightReporter
from .callables import CallablesReport, CallablesReporter
from .clusters import ClustersReport, ClustersReporter
from .coherence import CoherenceReport, CoherenceReporter
from .exports import ExportsReport, ExportsReporter
from .hotspots import HotspotsReport, HotspotsReporter


class InsightReport(ReportSection):
    report_id: str = "architecture.insights"
    report_title: str = "Architecture Insights"
    report_category: ReportCategory = ReportCategory.INSIGHTS
    report_path: str = "insights"
    report_order: int = 30
    report_children: tuple[type[ReportItem], ...] = Field(
        default=(
            ClustersReport,
            HotspotsReport,
            CoherenceReport,
            CallablesReport,
            ExportsReport,
        ),
        exclude=True,
    )

    clusters: ClustersReport = Field(default_factory=ClustersReport)
    hotspots: HotspotsReport = Field(default_factory=HotspotsReport)
    coherence: CoherenceReport = Field(default_factory=CoherenceReport)
    callables: CallablesReport = Field(default_factory=CallablesReport)
    exports: ExportsReport = Field(default_factory=ExportsReport)


@injectable
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

    def names(self) -> tuple[str, ...]:
        return tuple(self._reporters)


class InsightReportFieldMap:
    def field_for(self, reporter_name: str) -> str:
        if reporter_name == "unused-exports":
            return "exports"
        return reporter_name.replace("-", "_")


@injectable(lifetime="transient")
class InsightReportCollector:
    def __init__(
        self,
        catalog: InsightReporterCatalog,
        reporter_names: tuple[str, ...] = (),
    ):
        self.catalog = catalog
        self.reporter_names = reporter_names
        self.field_map = InsightReportFieldMap()

    def collect(self, architecture_map: ArchitectureMap) -> InsightReport:
        payload: dict[str, BaseModel] = {}
        for reporter_name in self.reporter_names or self.catalog.names():
            reporter = self.catalog.reporter(reporter_name)
            payload[self.field_map.field_for(reporter.name)] = reporter.collect(
                architecture_map
            )
        return InsightReport.model_validate(payload)
