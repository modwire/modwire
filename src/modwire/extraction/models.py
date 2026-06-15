from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..definitions import SourceFile
from ..graph import DependencyGraph, Edge
from .roots import SourceIdMode


@dataclass(frozen=True)
class ExtractionSummary:
    files_found: int
    files_checked: int
    files_excluded: int


@dataclass(frozen=True)
class ExtractionResult:
    files: dict[str, SourceFile]
    summary: ExtractionSummary


@dataclass(frozen=True)
class CodeMap:
    graph: DependencyGraph
    extraction_result: ExtractionResult
    runtime_command: str
    cache_status: str = "disabled"
    cache_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        from .serialization import serialize_code_map

        return serialize_code_map(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CodeMap:
        from .serialization import deserialize_code_map

        return deserialize_code_map(payload)

    @classmethod
    def from_json(cls, payload: str) -> CodeMap:
        return cls.from_dict(json.loads(payload))

    def source_ids(self) -> tuple[str, ...]:
        return tuple(self.extraction_result.files)

    def tracked_edges(self) -> tuple[Edge, ...]:
        return self.graph.tracked_edges(self.source_ids())

    def external_edges(self) -> tuple[Edge, ...]:
        return self.graph.external_edges(self.source_ids())

    def tracked_only(self) -> CodeMap:
        return self.subgraph(self.source_ids())

    def subgraph(self, node_ids: set[str] | tuple[str, ...]) -> CodeMap:
        selected = set(node_ids)
        files = {
            source_id: source_file
            for source_id, source_file in self.extraction_result.files.items()
            if source_id in selected
        }
        return CodeMap(
            graph=self.graph.subgraph(set(files)),
            extraction_result=ExtractionResult(
                files=files,
                summary=ExtractionSummary(
                    files_found=len(files),
                    files_checked=len(files),
                    files_excluded=0,
                ),
            ),
            runtime_command=self.runtime_command,
            cache_status=self.cache_status,
            cache_key=self.cache_key,
        )


@dataclass(frozen=True)
class SourceManifestEntry:
    source_id: str
    path: Path
    size: int
    mtime_ns: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "path": str(self.path),
            "size": self.size,
            "mtime_ns": self.mtime_ns,
        }


@dataclass(frozen=True)
class SourceManifest:
    language: str
    workspace_root: Path
    sources_root: Path
    source_id_root: str
    source_id_mode: SourceIdMode
    source_id_prefix: str
    exclusions: tuple[str, ...]
    file_extensions: tuple[str, ...]
    runtime_command: str
    runtime_path: str
    runtime_mtime_ns: int
    extractor_file: str
    extractor_path: Path
    extractor_mtime_ns: int
    modwire_version: str
    files_found: int
    files_checked: int
    files_excluded: int
    entries: tuple[SourceManifestEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "workspace_root": str(self.workspace_root),
            "sources_root": str(self.sources_root),
            "source_id_root": self.source_id_root,
            "source_id_mode": self.source_id_mode,
            "source_id_prefix": self.source_id_prefix,
            "exclusions": list(self.exclusions),
            "file_extensions": list(self.file_extensions),
            "runtime_command": self.runtime_command,
            "runtime_path": self.runtime_path,
            "runtime_mtime_ns": self.runtime_mtime_ns,
            "extractor_file": self.extractor_file,
            "extractor_path": str(self.extractor_path),
            "extractor_mtime_ns": self.extractor_mtime_ns,
            "modwire_version": self.modwire_version,
            "files_found": self.files_found,
            "files_checked": self.files_checked,
            "files_excluded": self.files_excluded,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    def fingerprint(self) -> str:
        from .manifest import manifest_fingerprint

        return manifest_fingerprint(self)
