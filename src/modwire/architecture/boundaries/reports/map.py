from wireup import injectable

from modwire.shared import ModwireBaseModel

from ...map.map import ArchitectureMap
from ...base import ReportCategory, ReportItem


class ArchitectureGroup(ModwireBaseModel):
    name: str
    source_ids: tuple[str, ...]


class ArchitectureMapReport(ReportItem):
    report_id: str = "architecture.map"
    report_title: str = "Architecture Map"
    report_category: ReportCategory = ReportCategory.MAP
    report_path: str = "map"
    report_order: int = 10

    modules: tuple[ArchitectureGroup, ...] = ()
    layers: tuple[ArchitectureGroup, ...] = ()
    unknown_files: tuple[str, ...] = ()


@injectable(lifetime="transient")
class ArchitectureMapReportCollector:
    def collect(self, architecture_map: ArchitectureMap) -> ArchitectureMapReport:
        return ArchitectureMapReport(
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
