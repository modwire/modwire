from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pydantic import BaseModel, ConfigDict

from modwire.modules import generate_module

PathLike = str | Path


class ProjectOperationPlan(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    operation: str
    paths: tuple[str, ...]
    dry_run: bool = False


class ProjectAuthority(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    project_name: str
    package_name: str
    profile: str
    language: str
    architecture: str
    module_scaffolding: str
    layout: dict[str, str]
    module_layout: dict[str, Any]
    operations: tuple[str, ...] = ()

    @property
    def module_mount(self) -> str:
        return self.layout["module_mount"]


def load_project_authority(project_root: PathLike) -> ProjectAuthority:
    authority_path = Path(project_root) / ".modwire" / "project.json"
    if not authority_path.exists():
        raise FileNotFoundError(f"Project authority does not exist: {authority_path}")

    payload = json.loads(authority_path.read_text(encoding="utf-8"))
    return ProjectAuthority.model_validate(payload)


def add_context(project_root: PathLike, context_name: str) -> ProjectOperationPlan:
    root = Path(project_root)
    authority = load_project_authority(root)
    _ensure_operation(authority, "add_context")
    context_path = _context_path(root, authority, context_name)
    touched = [
        _relative(root, context_path),
    ]

    context_path.mkdir(parents=True, exist_ok=True)
    for marker_root in _context_marker_roots(root, authority, context_name):
        marker_root.mkdir(parents=True, exist_ok=True)
        if _relative(root, marker_root) not in touched:
            touched.append(_relative(root, marker_root))

        for marker in _package_markers(authority):
            marker_path = marker_root / marker
            marker_path.touch(exist_ok=True)
            touched.append(_relative(root, marker_path))

    return ProjectOperationPlan(operation="add_context", paths=tuple(touched))


def add_module(
    project_root: PathLike,
    module_name: str,
    *,
    context_name: str | None = None,
    data: dict[str, Any] | None = None,
    overwrite: bool = False,
) -> ProjectOperationPlan:
    root = Path(project_root)
    authority = load_project_authority(root)
    _ensure_operation(authority, "add_module")

    context = context_name or module_name
    target_mount = root / authority.module_mount
    module_data = dict(data or {})
    module_data.setdefault("context_name", context)

    with TemporaryDirectory() as temp_dir:
        staged_root = Path(temp_dir)
        generate_module(
            module_name,
            staged_root,
            scaffolding=authority.module_scaffolding,
            data=module_data,
            overwrite=overwrite,
        )
        source_root = _language_output_root(staged_root, authority)
        created = _copy_tree(source_root, target_mount, overwrite=overwrite)

    return ProjectOperationPlan(operation="add_module", paths=created)


def remove_module(
    project_root: PathLike,
    module_name: str,
    *,
    context_name: str | None = None,
    dry_run: bool = False,
) -> ProjectOperationPlan:
    root = Path(project_root)
    authority = load_project_authority(root)
    _ensure_operation(authority, "remove_module")

    context = context_name or module_name
    module_path = _module_path(root, authority, context, module_name)
    paths = (_relative(root, module_path),)
    if not dry_run and module_path.exists():
        shutil.rmtree(module_path)

    return ProjectOperationPlan(
        operation="remove_module",
        paths=paths,
        dry_run=dry_run,
    )


def remove_context(
    project_root: PathLike,
    context_name: str,
    *,
    cascade: bool = False,
    dry_run: bool = False,
) -> ProjectOperationPlan:
    root = Path(project_root)
    authority = load_project_authority(root)
    _ensure_operation(authority, "remove_context")

    context_path = _context_path(root, authority, context_name)
    paths = (_relative(root, context_path),)

    if dry_run or not context_path.exists():
        return ProjectOperationPlan(
            operation="remove_context",
            paths=paths,
            dry_run=dry_run,
        )

    if not cascade and _has_module_children(context_path):
        raise ValueError(
            f"Context is not empty: {context_path}. Use cascade=True to remove it."
        )

    shutil.rmtree(context_path)
    return ProjectOperationPlan(operation="remove_context", paths=paths)


def _ensure_operation(authority: ProjectAuthority, operation: str) -> None:
    if operation not in authority.operations:
        raise ValueError(
            f"Project profile {authority.profile!r} does not allow {operation!r}"
        )


def _context_path(
    project_root: Path,
    authority: ProjectAuthority,
    context_name: str,
) -> Path:
    return _path_from_pattern(
        project_root,
        authority.module_layout["context_root"],
        _path_values(context_name=context_name),
    )


def _module_path(
    project_root: Path,
    authority: ProjectAuthority,
    context_name: str,
    module_name: str,
) -> Path:
    return _path_from_pattern(
        project_root,
        authority.module_layout["module_root"],
        _path_values(context_name=context_name, module_name=module_name),
    )


def _language_output_root(staged_root: Path, authority: ProjectAuthority) -> Path:
    scaffold_output_roots = authority.module_layout.get("scaffold_output_roots", {})
    try:
        scaffold_output_root = scaffold_output_roots[authority.language]
    except KeyError as error:
        known_languages = ", ".join(sorted(scaffold_output_roots))
        raise NotImplementedError(
            f"Project operations do not support language {authority.language!r}. "
            f"Known languages: {known_languages}"
        ) from error

    language_root = staged_root / scaffold_output_root
    if language_root.exists():
        return language_root
    return staged_root


def _context_marker_roots(
    project_root: Path,
    authority: ProjectAuthority,
    context_name: str,
) -> tuple[Path, ...]:
    return tuple(
        _path_from_pattern(
            project_root,
            marker_root,
            _path_values(context_name=context_name),
        )
        for marker_root in authority.module_layout.get("context_marker_roots", ())
    )


def _package_markers(authority: ProjectAuthority) -> tuple[str, ...]:
    markers = authority.module_layout.get("package_markers", {})
    return tuple(markers.get(authority.language, ()))


def _path_from_pattern(
    project_root: Path,
    pattern: str,
    values: dict[str, str],
) -> Path:
    return project_root / pattern.format(**values)


def _path_values(context_name: str, module_name: str = "") -> dict[str, str]:
    return {
        "context_name": context_name,
        "context_class_name": _pascal_case(context_name),
        "module_name": module_name,
        "module_class_name": _pascal_case(module_name),
    }


def _pascal_case(value: str) -> str:
    return "".join(
        part[:1].upper() + part[1:]
        for part in re.split(r"[^0-9A-Za-z]+", value)
        if part
    )


def _copy_tree(source_root: Path, target_root: Path, *, overwrite: bool) -> tuple[str, ...]:
    created: list[str] = []
    conflicts = [
        target_root / source.relative_to(source_root)
        for source in source_root.rglob("*")
        if source.is_file() and (target_root / source.relative_to(source_root)).exists()
    ]
    if conflicts and not overwrite:
        raise FileExistsError(f"Generated module path already exists: {conflicts[0]}")

    for source in sorted(source_root.rglob("*")):
        relative_path = source.relative_to(source_root)
        target = target_root / relative_path
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        created.append(str(relative_path))

    return tuple(created)


def _has_module_children(context_path: Path) -> bool:
    return any(
        child.is_dir() and child.name != "__pycache__"
        for child in context_path.iterdir()
    )


def _relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root))
