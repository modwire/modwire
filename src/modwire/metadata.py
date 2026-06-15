from __future__ import annotations

import hashlib
import inspect
import shutil
from dataclasses import dataclass
from pathlib import Path
from subprocess import run

from .extraction.serialization import CODE_MAP_SCHEMA_VERSION
from .extractors.loader import load_extractor, supported_languages


PUBLIC_API_STABILITY = "alpha"
EXTRACTION_SCHEMA_VERSION = CODE_MAP_SCHEMA_VERSION


class MissingRuntimeError(RuntimeError):
    """Raised when a language runtime command cannot be found."""


class ExtractorRuntimeError(RuntimeError):
    """Raised when an extractor runtime command fails."""


@dataclass(frozen=True)
class RuntimeInfo:
    command: str
    command_path: str = ""
    command_version: str = ""
    available: bool = False
    exit_code: int = 0
    stderr: str = ""


@dataclass(frozen=True)
class LanguageInfo:
    name: str
    file_extensions: tuple[str, ...]
    command: str
    extractor_file: str
    extractor_path: Path
    implementation_stamp: str
    runtime: RuntimeInfo


def languages() -> tuple[LanguageInfo, ...]:
    return tuple(language(name) for name in supported_languages())


def language(name: str) -> LanguageInfo:
    extractor = load_extractor(name)
    extractor_path = _extractor_script_path(extractor.extractor_file)
    return LanguageInfo(
        name=extractor.language,
        file_extensions=extractor.file_extensions,
        command=extractor.command,
        extractor_file=extractor.extractor_file,
        extractor_path=extractor_path,
        implementation_stamp=extraction_implementation_stamp(name),
        runtime=runtime_diagnostics(name),
    )


def runtime_diagnostics(name: str) -> RuntimeInfo:
    extractor = load_extractor(name)
    command_path = shutil.which(extractor.command) or ""
    if command_path == "":
        return RuntimeInfo(
            command=extractor.command,
            available=False,
            exit_code=127,
            stderr=f"Runtime command not found: {extractor.command}",
        )

    result = run(
        [command_path, "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    version = (result.stdout or result.stderr).strip().splitlines()
    return RuntimeInfo(
        command=extractor.command,
        command_path=command_path,
        command_version=version[0] if version else "",
        available=result.returncode == 0,
        exit_code=result.returncode,
        stderr=result.stderr.strip(),
    )


def extraction_implementation_stamp(name: str) -> str:
    extractor = load_extractor(name)
    hasher = hashlib.sha256()
    for path in (
        Path(inspect.getfile(type(extractor))).resolve(),
        _extractor_script_path(extractor.extractor_file),
    ):
        hasher.update(path.as_posix().encode("utf-8"))
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def require_runtime(name: str) -> RuntimeInfo:
    diagnostics = runtime_diagnostics(name)
    if not diagnostics.available:
        raise MissingRuntimeError(diagnostics.stderr)
    return diagnostics


def _extractor_script_path(extractor_file: str) -> Path:
    return (Path(__file__).parent / "extractors" / "scripts" / extractor_file).resolve()


__all__ = [
    "EXTRACTION_SCHEMA_VERSION",
    "PUBLIC_API_STABILITY",
    "ExtractorRuntimeError",
    "LanguageInfo",
    "MissingRuntimeError",
    "RuntimeInfo",
    "extraction_implementation_stamp",
    "language",
    "languages",
    "require_runtime",
    "runtime_diagnostics",
]
