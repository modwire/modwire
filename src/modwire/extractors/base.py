from __future__ import annotations

import json
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from subprocess import run
from typing import Protocol

from ..definitions import SourceExport, SourceFile, SourceImport


@dataclass(frozen=True)
class SourceExtraction:
    files: dict[str, SourceFile]
    files_found: int
    files_excluded: int


@dataclass(frozen=True)
class ExtractionTarget:
    source_id: str
    path: Path


class SourceExtractor(Protocol):
    language: str
    file_extensions: tuple[str, ...]
    command: str
    extractor_file: str

    def normalize_source_id(self, value: str) -> str:
        source_id = value.strip().strip("/")
        for file_extension in self.file_extensions:
            if source_id.endswith(file_extension):
                return source_id[: -len(file_extension)]
        return source_id

    def normalize_import(
        self,
        source_id: str,
        source_import: SourceImport,
        known_source_ids: set[str],
    ) -> SourceImport:
        if source_import.normalized_path in known_source_ids:
            return source_import
        return SourceImport(
            path=source_import.path,
            is_relative=source_import.is_relative,
            normalized_path=source_import.normalized_path.strip().strip("/"),
            imported_name=source_import.imported_name,
            is_aliased=source_import.is_aliased,
            crossing_type=source_import.crossing_type,
            file_barrier_crossed=False,
            statement_id=source_import.statement_id,
            join_key=source_import.join_key,
            uses_joined_import=source_import.uses_joined_import,
            imported_symbols=source_import.imported_symbols,
        )

    def normalize_export(
        self,
        source_id: str,
        source_export: SourceExport,
        known_source_ids: set[str],
    ) -> SourceExport:
        return SourceExport(
            name=source_export.name,
            local_name=source_export.local_name,
            kind=source_export.kind,
            crossing_type=source_export.crossing_type,
            path=source_export.path,
            is_relative=source_export.is_relative,
            normalized_path=source_export.normalized_path.strip().strip("/"),
            is_reexport=source_export.is_reexport,
            is_default=source_export.is_default,
            is_aliased=source_export.is_aliased,
            statement_id=source_export.statement_id,
        )

    def extract_files(
        self,
        sources_root: Path,
        exclusions: tuple[str, ...],
        source_id_prefix: str = "",
    ) -> SourceExtraction:
        script = Path(__file__).parent / "scripts" / self.extractor_file
        assert script.is_file(), f"Extractor script {script} not found"

        targets, files_found, files_excluded = _collect_extraction_targets(
            sources_root,
            self.file_extensions,
            exclusions,
        )
        if not targets:
            return SourceExtraction(
                files={},
                files_found=files_found,
                files_excluded=files_excluded,
            )

        input_data = {
            self.normalize_source_id(
                _join_source_id(source_id_prefix, target.source_id)
            ): str(target.path.resolve())
            for target in targets
        }
        cmd = [self.command, str(script), "--batch", str(sources_root.resolve())]
        raw_files = _json_from_output(cmd, json.dumps(input_data))
        result = {
            source_id: SourceFile.model_validate(source_file)
            for source_id, source_file in raw_files.items()
        }

        known_source_ids = set(result)
        result = {
            source_id: self.normalize_source_file(
                source_id,
                source_file,
                known_source_ids,
            )
            for source_id, source_file in result.items()
        }

        return SourceExtraction(
            files=result,
            files_found=files_found,
            files_excluded=files_excluded,
        )

    def normalize_source_file(
        self,
        source_id: str,
        source_file: SourceFile,
        known_source_ids: set[str],
    ) -> SourceFile:
        exports = [
            self.normalize_export(source_id, source_export, known_source_ids)
            for source_export in source_file.exports
        ]
        exports = self._with_module_export(source_id, exports)

        return SourceFile(
            imports=[
                self.normalize_import(source_id, source_import, known_source_ids)
                for source_import in source_file.imports
            ],
            exports=exports,
            classes=source_file.classes,
            interfaces=source_file.interfaces,
            types=source_file.types,
            abstract_classes=source_file.abstract_classes,
            functions=source_file.functions,
            line_count=source_file.line_count,
            code_line_count=source_file.code_line_count,
            public_symbol_count=source_file.public_symbol_count,
        )

    def _with_module_export(
        self,
        source_id: str,
        exports: list[SourceExport],
    ) -> list[SourceExport]:
        module_export = SourceExport(
            name=source_id,
            local_name=source_id,
            kind="module",
            crossing_type="module",
            path=source_id,
            is_relative=False,
            normalized_path=source_id,
            is_reexport=False,
            is_default=False,
            is_aliased=False,
            statement_id=0,
        )
        seen = {
            (
                source_export.name,
                source_export.kind,
                source_export.crossing_type,
                source_export.normalized_path,
            )
            for source_export in exports
        }
        module_key = (
            module_export.name,
            module_export.kind,
            module_export.crossing_type,
            module_export.normalized_path,
        )
        if module_key in seen:
            return exports
        return [module_export, *exports]


def _collect_extraction_targets(
    sources_root: Path,
    file_extensions: tuple[str, ...],
    exclusions: tuple[str, ...],
) -> tuple[tuple[ExtractionTarget, ...], int, int]:
    directory_exclusions, file_exclusions = _partition_exclusions(
        exclusions,
        file_extensions,
    )
    targets: list[ExtractionTarget] = []
    files_found = 0
    files_excluded = 0

    def walk(directory: Path, relative_dir: str = "") -> None:
        nonlocal files_found, files_excluded
        directories: list[tuple[str, Path]] = []
        files: list[tuple[str, Path]] = []

        for entry in sorted(directory.iterdir(), key=lambda path: path.name):
            source_id = (
                f"{relative_dir}/{entry.name}" if relative_dir else entry.name
            )
            if entry.is_dir() and not entry.is_symlink():
                if _matches_directory_exclusion(source_id, directory_exclusions):
                    # Exact file counts would require descending into the pruned tree.
                    files_found += 1
                    files_excluded += 1
                    continue
                directories.append((source_id, entry))
                continue

            if entry.is_file() and entry.suffix in file_extensions:
                files.append((source_id, entry))

        for source_id, path in files:
            files_found += 1
            if any(
                _matches_exclusion(source_id, exclusion)
                for exclusion in file_exclusions
            ):
                files_excluded += 1
                continue

            targets.append(ExtractionTarget(source_id, path))

        for source_id, path in directories:
            walk(path, source_id)

    walk(sources_root)

    return tuple(targets), files_found, files_excluded


def _json_from_output(cmd: list[str], input_json: str = "") -> dict:
    output_json = run(
        cmd,
        capture_output=True,
        text=True,
        input=input_json,
        check=True,
    ).stdout

    try:
        return json.loads(output_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from output: {output_json}") from e


def _matches_exclusion(source_id: str, exclusion: str) -> bool:
    normalized = exclusion.replace("\\", "/").strip().strip("/")
    if not normalized:
        return False

    if _matches_path_pattern(source_id, normalized):
        return True

    has_glob = any(char in normalized for char in "*?[")
    if not normalized or has_glob:
        return False

    return source_id.startswith(f"{normalized}/")


def _partition_exclusions(
    exclusions: tuple[str, ...],
    file_extensions: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    directory_exclusions = []
    file_exclusions = []
    for exclusion in exclusions:
        normalized = exclusion.replace("\\", "/").strip()
        if not normalized:
            continue
        if _is_recursive_directory_exclusion(normalized, file_extensions):
            directory_exclusions.append(_directory_exclusion_pattern(normalized))
        else:
            file_exclusions.append(normalized.strip("/"))
    return tuple(directory_exclusions), tuple(file_exclusions)


def _is_recursive_directory_exclusion(
    exclusion: str,
    file_extensions: tuple[str, ...],
) -> bool:
    normalized = exclusion.strip("/")
    if not normalized:
        return False
    if exclusion.endswith("/") or normalized.endswith("/**"):
        return True
    if any(char in normalized for char in "*?["):
        return False
    return not normalized.endswith(file_extensions)


def _directory_exclusion_pattern(exclusion: str) -> str:
    normalized = exclusion.strip("/")
    if normalized.endswith("/**"):
        return normalized[:-3].rstrip("/")
    return normalized


def _matches_directory_exclusion(
    source_id: str,
    directory_exclusions: tuple[str, ...],
) -> bool:
    for exclusion in directory_exclusions:
        if _matches_path_pattern(source_id, exclusion):
            return True
        if "/" not in exclusion and not any(char in exclusion for char in "*?["):
            if Path(source_id).name == exclusion:
                return True
    return False


def _matches_path_pattern(source_id: str, pattern: str) -> bool:
    if fnmatch(source_id, pattern):
        return True
    if pattern.startswith("**/") and fnmatch(source_id, pattern[3:]):
        return True
    return False


def _join_source_id(prefix: str, source_id: str) -> str:
    normalized_prefix = prefix.replace("\\", "/").strip().strip("/")
    normalized_source_id = source_id.replace("\\", "/").strip().strip("/")
    if not normalized_prefix:
        return normalized_source_id
    if not normalized_source_id:
        return normalized_prefix
    return f"{normalized_prefix}/{normalized_source_id}"


__all__ = [
    "ExtractionTarget",
    "SourceExtraction",
    "SourceExtractor",
]
