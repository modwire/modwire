from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Any

import copier

from .profile import get_project_profile

PathLike = str | Path


@contextmanager
def _bundled_scaffolding_path(profile: str) -> Iterator[Path]:
    scaffoldings = resources.files("modwire.projects") / "scaffoldings" / profile
    with resources.as_file(scaffoldings) as path:
        yield path


def generate_project(
    project_name: str,
    target_root: PathLike,
    template_root: PathLike | None = None,
    *,
    profile: str = "python-fastapi-ddd-uv",
    data: Mapping[str, Any] | None = None,
    overwrite: bool = False,
    skip_tasks: bool = True,
) -> None:
    project_profile = get_project_profile(profile)
    template_data = _template_data(project_name, project_profile, data)

    if template_root is not None:
        _run_copy(
            Path(template_root),
            target_root,
            template_data,
            overwrite=overwrite,
            skip_tasks=skip_tasks,
        )
        return

    with _bundled_scaffolding_path(profile) as resolved_template_root:
        _run_copy(
            resolved_template_root,
            target_root,
            template_data,
            overwrite=overwrite,
            skip_tasks=skip_tasks,
        )


def _template_data(
    project_name: str,
    project_profile: Any,
    data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    package_name = _package_name(project_name)
    template_data: dict[str, Any] = {
        "project_name": project_name,
        "package_name": package_name,
        "profile_name": project_profile.name,
        "architecture": project_profile.architecture,
        "module_scaffolding": project_profile.module_scaffolding,
        "language": project_profile.toolchain.language,
        "language_version": project_profile.toolchain.language_version,
        "package_manager": project_profile.toolchain.package_manager,
        "framework": project_profile.toolchain.framework,
        "dependencies": project_profile.toolchain.dependencies,
        "dev_dependencies": project_profile.toolchain.dev_dependencies,
        "scripts": {
            name: command.format(package_name=package_name)
            for name, command in project_profile.toolchain.scripts.items()
        },
        "operations": project_profile.operations,
    }
    template_data.update(data or {})

    package_name = str(template_data["package_name"])
    authority = project_profile.resolved_authority(project_name, package_name)
    authority["scripts"] = {
        name: command.format(package_name=package_name)
        for name, command in project_profile.toolchain.scripts.items()
    }
    template_data["project_authority_json"] = json.dumps(
        authority,
        indent=2,
        sort_keys=True,
    )
    return template_data


def _run_copy(
    template_root: Path,
    target_root: PathLike,
    data: Mapping[str, Any],
    *,
    overwrite: bool,
    skip_tasks: bool,
) -> None:
    resolved_template_root = template_root
    if not resolved_template_root.exists():
        raise FileNotFoundError(f"Copier template does not exist: {resolved_template_root}")

    copier.run_copy(
        str(resolved_template_root),
        dst_path=target_root,
        data=dict(data),
        defaults=True,
        overwrite=overwrite,
        skip_tasks=skip_tasks,
    )


def _package_name(project_name: str) -> str:
    package_name = re.sub(r"\W+", "_", project_name.strip().lower())
    package_name = re.sub(r"_+", "_", package_name).strip("_")
    return package_name or "app"


__all__ = ["generate_project"]
