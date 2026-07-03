from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from modwire.shared import ModwireBaseModel

from ...report import ReportCategory, ReportItem


if TYPE_CHECKING:
    from ...boundaries import ArchitectureMap
    from ..base import ShapeResolver


class ShapeViolation(ModwireBaseModel):
    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    symbol_kind: str = ""
    symbol_name: str = ""


class ShapeReport(ReportItem):
    report_id: ClassVar[str] = "architecture.violations.shape"
    report_title: ClassVar[str] = "Shape Violations"
    report_category: ClassVar[ReportCategory] = ReportCategory.SHAPE
    report_path: ClassVar[str] = "violations.shape"
    report_order: ClassVar[int] = 20

    violations: tuple[ShapeViolation, ...] = ()
    resolvers: tuple[str, ...] = ()


class ShapeResolverCatalog:
    def __init__(self):
        self._resolvers = {
            resolver.name: resolver
            for resolver in self.default_resolvers()
        }

    def resolver(self, name: str) -> "ShapeResolver":
        try:
            return self._resolvers[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._resolvers))
            raise ValueError(
                f"Unknown shape resolver {name!r}. Known resolvers: {known}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._resolvers)

    @classmethod
    def default_resolvers(cls) -> tuple["ShapeResolver", ...]:
        from ..rules import (
            AbstractClassResolver,
            CallableResolver,
            ClassResolver,
            FileResolver,
            ImportResolver,
            PropertyResolver,
            SignatureResolver,
            SymbolResolver,
        )

        return (
            FileResolver(),
            ClassResolver(),
            AbstractClassResolver(),
            CallableResolver(),
            SignatureResolver(),
            PropertyResolver(),
            ImportResolver(),
            SymbolResolver(),
        )


class ShapeReportCollector:
    def __init__(self, catalog: ShapeResolverCatalog | None = None):
        self.catalog = catalog or ShapeResolverCatalog()

    def collect(
        self,
        architecture_map: ArchitectureMap,
        resolver_names: tuple[str, ...],
    ) -> ShapeReport:
        violations: list[ShapeViolation] = []
        config = architecture_map.config.shape
        for resolver_name in resolver_names:
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
            resolvers=resolver_names,
        )
