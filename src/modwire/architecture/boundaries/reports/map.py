from typing import ClassVar

from modwire.shared import ModwireBaseModel

from ...map.map import ArchitectureMap
from ...base import ReportCategory, ReportItem


class ArchitectureGroup(ModwireBaseModel):
    name: str
    source_ids: tuple[str, ...]


class ArchitectureMapReport(ReportItem):
    report_id: ClassVar[str] = "architecture.map"
    report_title: ClassVar[str] = "Architecture Map"
    report_category: ClassVar[ReportCategory] = ReportCategory.MAP
    report_path: ClassVar[str] = "map"
    report_order: ClassVar[int] = 10

    modules: tuple[ArchitectureGroup, ...] = ()
    layers: tuple[ArchitectureGroup, ...] = ()
    unknown_files: tuple[str, ...] = ()


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
