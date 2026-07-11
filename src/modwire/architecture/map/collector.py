from modwire.shared import ModwireModel, report

from .base import ArchitectureMap


class ArchitectureGroup(ModwireModel):
    name: str
    source_ids: tuple[str, ...]


class MapReport(report.ReportItem):
    report_id: str = "architecture.map"
    report_title: str = "Architecture Map"
    report_description: str = (
        "Groups source files by configured architecture modules and layers, "
        "and lists files that were not matched by the architecture map."
    )
    report_path: str = "map"
    report_order: int = 10

    modules: tuple[ArchitectureGroup, ...] = ()
    layers: tuple[ArchitectureGroup, ...] = ()
    unknown_files: tuple[str, ...] = ()


class MapReportCollector(report.ReportCollector[MapReport]):
    report_type: type[MapReport] = MapReport

    def collect(self, architecture_map: ArchitectureMap) -> MapReport:
        return self.report_type(
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
