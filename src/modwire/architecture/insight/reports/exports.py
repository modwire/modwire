from pydantic import BaseModel, ConfigDict

from ...boundaries.map import ArchitectureMap

from ..base import InsightReporter


class UnusedExport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_id: str
    name: str
    kind: str
    crossing_type: str
    reason: str


class UnusedExportInsight(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    unused_exports: tuple[UnusedExport, ...] = ()


class ExportsReporter(InsightReporter):
    name: str = "unused-exports"
    title: str = "Unused Exports"

    def collect(self, architecture_map: ArchitectureMap) -> UnusedExportInsight:
        imported_names = self.imported_names(architecture_map)
        unused_exports = tuple(
            UnusedExport(
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
        return UnusedExportInsight(unused_exports=unused_exports)

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


__all__ = [
    "ExportsReporter",
    "UnusedExport",
    "UnusedExportInsight",
]
