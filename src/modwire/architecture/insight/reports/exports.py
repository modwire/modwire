from typing import TYPE_CHECKING, ClassVar

from modwire.shared import ModwireBaseModel

from ...report import ReportCategory, ReportItem

from ..base import InsightReporter


if TYPE_CHECKING:
    from ...boundaries import ArchitectureMap


class ExportsReportItem(ModwireBaseModel):
    source_id: str
    name: str
    kind: str
    crossing_type: str
    reason: str


class ExportsReport(ReportItem):
    report_id: ClassVar[str] = "architecture.insights.exports"
    report_title: ClassVar[str] = "Unused Exports"
    report_category: ClassVar[ReportCategory] = ReportCategory.INSIGHT
    report_path: ClassVar[str] = "insights.exports"
    report_order: ClassVar[int] = 50

    unused_exports: tuple[ExportsReportItem, ...] = ()


class ExportsReporter(InsightReporter):
    name: str = "unused-exports"
    title: str = "Unused Exports"

    def collect(self, architecture_map: ArchitectureMap) -> ExportsReport:
        imported_names = self.imported_names(architecture_map)
        unused_exports = tuple(
            ExportsReportItem(
                source_id=export_result.source_id,
                name=export.name,
                kind=export.kind,
                crossing_type=export.crossing_type,
                reason="not imported",
            )
            for export_result in sorted(
                architecture_map.code_map.exports().all(),
                key=lambda result: (result.source_id, result.item.name),
            )
            if (export := export_result.item).name not in imported_names
            and export.local_name not in imported_names
        )
        return ExportsReport(unused_exports=unused_exports)

    def imported_names(self, architecture_map: ArchitectureMap) -> set[str]:
        imported_names: set[str] = set()
        for import_result in architecture_map.code_map.imports().all():
            imported_name = import_result.item.imported_name
            if imported_name:
                imported_names.add(imported_name)
            for imported_symbol in import_result.item.imported_symbols:
                imported_names.add(imported_symbol.name)
                if imported_symbol.alias:
                    imported_names.add(imported_symbol.alias)
        return imported_names
