from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from .base import ShapeResolver, ShapeViolation
from .rules import (
    AbstractClassResolver,
    CallableResolver,
    ClassResolver,
    FileResolver,
    ImportResolver,
    PropertyResolver,
    SignatureResolver,
    SymbolResolver,
)

if TYPE_CHECKING:
    from ..boundaries.map import ArchitectureMap


class ShapeReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violations: tuple[ShapeViolation, ...] = ()
    resolvers: tuple[str, ...] = ()


class ShapePipelineStepInterface(ABC):
    @abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> ShapeReport:
        raise NotImplementedError


class ShapeResolverCatalog:
    def __init__(self):
        self._resolvers = {
            resolver.name: resolver
            for resolver in (
                FileResolver(),
                ClassResolver(),
                AbstractClassResolver(),
                CallableResolver(),
                SignatureResolver(),
                PropertyResolver(),
                ImportResolver(),
                SymbolResolver(),
            )
        }

    def resolver(self, name: str) -> ShapeResolver:
        try:
            return self._resolvers[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._resolvers))
            raise ValueError(
                f"Unknown shape resolver {name!r}. Known resolvers: {known}"
            ) from exc


class ShapePipelineStep(ShapePipelineStepInterface):
    def __init__(
        self,
        resolvers: tuple[str, ...]
    ):
        self.catalog = ShapeResolverCatalog()
        self.resolvers = resolvers

    def run(self, architecture_map: ArchitectureMap) -> ShapeReport:
        violations: list[ShapeViolation] = []
        config = architecture_map.config.shape
        for resolver_name in self.resolvers:
            resolver = self.catalog.resolver(resolver_name)
            for source_file in architecture_map.code_map.source_files().all():
                violations.extend(
                    resolver.resolve(
                        source_file.source_id,
                        source_file.file,
                        config,
                    )
                )
        return ShapeReport(
            violations=tuple(violations),
            resolvers=self.resolvers,
        )


__all__ = [
    "ShapePipelineStep",
    "ShapePipelineStepInterface",
    "ShapeReport",
    "ShapeResolverCatalog",
]
