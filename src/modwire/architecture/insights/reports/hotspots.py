from modwire.shared import ModwireBaseModel

from ...map.map import ArchitectureMap
from ...base import ReportCategory, ReportItem
from .base import InsightReporter


class HotspotsReportItem(ModwireBaseModel):
    source_id: str
    incoming_count: int
    outgoing_count: int
    pressure_score: int


class HotspotsReport(ReportItem):
    report_id: str = "architecture.insights.hotspots"
    report_title: str = "Dependency Hotspots"
    report_category: ReportCategory = ReportCategory.INSIGHT
    report_path: str = "insights.hotspots"
    report_order: int = 20

    hotspots: tuple[HotspotsReportItem, ...] = ()


class HotspotsReporter(InsightReporter):
    name: str = "hotspots"
    title: str = "Dependency Hotspots"

    def collect(self, architecture_map: ArchitectureMap) -> HotspotsReport:
        hotspots = tuple(
            sorted(
                (
                    self.hotspot_for(architecture_map, source_id)
                    for source_id in architecture_map.code_map.source_ids()
                ),
                key=lambda hotspot: (
                    -hotspot.pressure_score,
                    hotspot.source_id,
                ),
            )
        )
        return HotspotsReport(hotspots=hotspots)

    def hotspot_for(
        self,
        architecture_map: ArchitectureMap,
        source_id: str,
    ) -> HotspotsReportItem:
        incoming_count = architecture_map.code_map.incoming_dependencies(
            source_id
        ).count()
        outgoing_count = architecture_map.code_map.outgoing_dependencies(
            source_id
        ).count()
        return HotspotsReportItem(
            source_id=source_id,
            incoming_count=incoming_count,
            outgoing_count=outgoing_count,
            pressure_score=incoming_count + outgoing_count,
        )
