from pydantic import Field

from ...base import ReportCategory, ReportItem, ReportSection

from .callables import CallablesReport
from .clusters import ClustersReport
from .coherence import CoherenceReport
from .exports import ExportsReport
from .hotspots import HotspotsReport


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


class InsightReportFieldMap:
    def field_for(self, reporter_name: str) -> str:
        if reporter_name == "unused-exports":
            return "exports"
        return reporter_name.replace("-", "_")
