from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Any

import copier

PathLike = str | Path


@contextmanager
def _bundled_scaffolding_path(scaffolding: str) -> Iterator[Path]:
    scaffoldings = resources.files("modwire.modules") / "scaffoldings" / scaffolding
    with resources.as_file(scaffoldings) as path:
        yield path


def generate_module(
    module_name: str,
    target_root: PathLike,
    template_root: PathLike | None = None,
    *,
    scaffolding: str = "layered",
    data: Mapping[str, Any] | None = None,
    overwrite: bool = False,
    skip_tasks: bool = True,
) -> None:
    if template_root is not None:
        _run_copy(
            Path(template_root),
            target_root,
            module_name,
            data=data,
            overwrite=overwrite,
            skip_tasks=skip_tasks,
        )
        return

    with _bundled_scaffolding_path(scaffolding) as resolved_template_root:
        _run_copy(
            resolved_template_root,
            target_root,
            module_name,
            data=data,
            overwrite=overwrite,
            skip_tasks=skip_tasks,
        )


def _run_copy(
    template_root: Path,
    target_root: PathLike,
    module_name: str,
    *,
    data: Mapping[str, Any] | None,
    overwrite: bool,
    skip_tasks: bool,
) -> None:
    resolved_template_root = template_root
    if not resolved_template_root.exists():
        raise FileNotFoundError(f"Copier template does not exist: {resolved_template_root}")

    template_data = dict(data or {})
    template_data["module_name"] = module_name

    copier.run_copy(
        str(resolved_template_root),
        dst_path=target_root,
        data=template_data,
        defaults=True,
        overwrite=overwrite,
        skip_tasks=skip_tasks,
    )
