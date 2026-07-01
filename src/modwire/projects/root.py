from __future__ import annotations

from pathlib import Path
from typing import Any

from . import _operations

PathLike = str | Path


class ProjectRoot:
    def __init__(self, project_root: PathLike):
        self.project_root = Path(project_root)

    def authority(self) -> _operations.ProjectAuthority:
        return _operations.load_project_authority(self.project_root)

    def add_context(self, context_name: str) -> _operations.ProjectOperationPlan:
        return _operations.add_context(self.project_root, context_name)

    def add_module(
        self,
        module_name: str,
        *,
        context_name: str | None = None,
        data: dict[str, Any] | None = None,
        overwrite: bool = False,
    ) -> _operations.ProjectOperationPlan:
        return _operations.add_module(
            self.project_root,
            module_name,
            context_name=context_name,
            data=data,
            overwrite=overwrite,
        )

    def remove_module(
        self,
        module_name: str,
        *,
        context_name: str | None = None,
        dry_run: bool = False,
    ) -> _operations.ProjectOperationPlan:
        return _operations.remove_module(
            self.project_root,
            module_name,
            context_name=context_name,
            dry_run=dry_run,
        )

    def remove_context(
        self,
        context_name: str,
        *,
        cascade: bool = False,
        dry_run: bool = False,
    ) -> _operations.ProjectOperationPlan:
        return _operations.remove_context(
            self.project_root,
            context_name,
            cascade=cascade,
            dry_run=dry_run,
        )


def open_project(project_root: PathLike) -> ProjectRoot:
    return ProjectRoot(project_root)


__all__ = ["ProjectRoot", "open_project"]
