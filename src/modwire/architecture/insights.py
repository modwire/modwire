from __future__ import annotations

from dataclasses import dataclass

from .matching import TagMap


@dataclass(frozen=True)
class CrossModuleDependency:
    source: str
    target: str
    count: int


@dataclass(frozen=True)
class ArchitectureMap:
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]
    cross_module_dependencies: tuple[CrossModuleDependency, ...]
