from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from .._version import __version__
from ..extractors import load_extractor
from ..extractors.base import _collect_extraction_targets
from .models import SourceManifest, SourceManifestEntry


def discover_sources(
    language: str,
    sources_root: Path,
    exclusions: tuple[str, ...] = (),
) -> SourceManifest:
    """Return the source manifest using the same traversal as extraction."""
    assert sources_root.is_dir(), f"Project root {sources_root} is not a directory"

    extractor = load_extractor(language)
    targets, files_found, files_excluded = _collect_extraction_targets(
        sources_root,
        extractor.file_extensions,
        exclusions,
    )
    entries = []
    for target in targets:
        stat = target.path.stat()
        entries.append(
            SourceManifestEntry(
                source_id=extractor.normalize_source_id(target.source_id),
                path=target.path.resolve(),
                size=stat.st_size,
                mtime_ns=stat.st_mtime_ns,
            )
        )
    extractor_path = (
        Path(__file__).parents[1] / "extractors" / "scripts" / extractor.extractor_file
    ).resolve()
    runtime_path = shutil.which(extractor.command)
    runtime_mtime_ns = None
    if runtime_path is not None:
        runtime_mtime_ns = Path(runtime_path).stat().st_mtime_ns

    return SourceManifest(
        language=language,
        sources_root=sources_root.resolve(),
        exclusions=tuple(exclusions),
        file_extensions=extractor.file_extensions,
        runtime_command=extractor.command,
        runtime_path=runtime_path,
        runtime_mtime_ns=runtime_mtime_ns,
        extractor_file=extractor.extractor_file,
        extractor_path=extractor_path,
        extractor_mtime_ns=extractor_path.stat().st_mtime_ns,
        modwire_version=__version__,
        files_found=files_found,
        files_checked=len(entries),
        files_excluded=files_excluded,
        entries=tuple(entries),
    )


def manifest_fingerprint(manifest: SourceManifest) -> str:
    payload = json.dumps(manifest.to_dict(), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
