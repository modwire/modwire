from __future__ import annotations

from dataclasses import dataclass

from .definitions import SourceExport, SourceImportedSymbol, SourceImport


@dataclass(frozen=True)
class UnusedExport:
    source_id: str
    name: str
    kind: str
    crossing_type: str
    reason: str


def find_unused_exports(
    extraction_result,
) -> tuple[UnusedExport, ...]:
    files = source_files(extraction_result)
    exports_by_source = {
        source_id: tuple(source_file.exports)
        for source_id, source_file in files.items()
    }
    export_index: dict[tuple[str, str, str], list[SourceExport]] = {}
    module_exports: dict[str, list[SourceExport]] = {}
    star_reexports: dict[str, list[SourceExport]] = {}

    for source_id, source_exports in exports_by_source.items():
        for source_export in source_exports:
            export_index.setdefault(
                (source_id, source_export.name, source_export.crossing_type),
                [],
            ).append(source_export)
            if source_export.kind == "module" and source_export.crossing_type == "module":
                module_exports.setdefault(source_id, []).append(source_export)
            if (
                source_export.is_reexport
                and source_export.crossing_type == "module"
                and source_export.name == "*"
            ):
                star_reexports.setdefault(source_id, []).append(source_export)

    used: set[tuple[str, str, str, str, str, bool]] = set()

    def mark_export(source_id: str, source_export: SourceExport) -> None:
        key = _export_key(source_id, source_export)
        if key in used:
            return
        used.add(key)
        if not source_export.is_reexport:
            return
        if source_export.normalized_path not in files:
            return
        mark_module(source_export.normalized_path)
        if source_export.crossing_type == "symbol":
            mark_symbol(
                source_export.normalized_path,
                source_export.local_name,
            )

    def mark_module(source_id: str) -> None:
        for source_export in module_exports.get(source_id, ()):
            mark_export(source_id, source_export)

    def mark_symbol(source_id: str, name: str) -> None:
        matched_exports = export_index.get((source_id, name, "symbol"), [])
        if matched_exports:
            for source_export in matched_exports:
                mark_export(source_id, source_export)
            return

        for source_export in star_reexports.get(source_id, ()):
            mark_export(source_id, source_export)
            if source_export.normalized_path in files:
                mark_module(source_export.normalized_path)
                mark_symbol(source_export.normalized_path, name)

    def mark_all_symbols(source_id: str) -> None:
        for source_export in exports_by_source.get(source_id, ()):
            if source_export.crossing_type == "symbol":
                mark_export(source_id, source_export)

    for source_id, source_file in files.items():
        for source_import in source_file.imports:
            target_id = source_import.normalized_path
            if target_id not in files or target_id == source_id:
                continue

            symbols = _imported_symbols(source_import)
            if source_import.crossing_type == "symbol" and symbols:
                usable_symbols = [
                    symbol
                    for symbol in symbols
                    if not _is_reexport_plumbing(
                        exports_by_source.get(source_id, ()),
                        target_id,
                        symbol,
                    )
                ]
                if not usable_symbols:
                    continue
                mark_module(target_id)
                for symbol in usable_symbols:
                    if symbol.is_namespace:
                        continue
                    if symbol.is_star or symbol.name == "*":
                        mark_all_symbols(target_id)
                    else:
                        mark_symbol(target_id, symbol.name)
                continue

            mark_module(target_id)

    unused = []
    for source_id, source_exports in exports_by_source.items():
        for source_export in source_exports:
            if _export_key(source_id, source_export) in used:
                continue
            unused.append(
                UnusedExport(
                    source_id=source_id,
                    name=source_export.name,
                    kind=source_export.kind,
                    crossing_type=source_export.crossing_type,
                    reason="export is not imported by another source file",
                )
            )

    return tuple(unused)


def _imported_symbols(source_import: SourceImport) -> tuple[SourceImportedSymbol, ...]:
    if source_import.imported_symbols:
        return tuple(source_import.imported_symbols)
    if not source_import.imported_name:
        return ()
    return (
        SourceImportedSymbol(
            name=source_import.imported_name,
            alias="",
            is_aliased=False,
            is_default=False,
            is_namespace=False,
            is_star=source_import.imported_name == "*",
        ),
    )


def _is_reexport_plumbing(
    source_exports: tuple[SourceExport, ...],
    target_id: str,
    symbol: SourceImportedSymbol,
) -> bool:
    for source_export in source_exports:
        if not source_export.is_reexport or source_export.normalized_path != target_id:
            continue
        if source_export.name == "*":
            return True
        if source_export.local_name == symbol.name or source_export.name == symbol.name:
            return True
    return False


def _export_key(
    source_id: str,
    source_export: SourceExport,
) -> tuple[str, str, str, str, str, bool]:
    return (
        source_id,
        source_export.name,
        source_export.crossing_type,
        source_export.normalized_path,
        source_export.local_name,
        source_export.is_reexport,
    )


__all__ = ["UnusedExport", "find_unused_exports"]
