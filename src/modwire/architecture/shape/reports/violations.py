from typing import TYPE_CHECKING, ClassVar

from modwire.shared import ModwireBaseModel

from ...base import ReportCategory, ReportItem
from ..config import ShapeConfig


if TYPE_CHECKING:
    from ...map import ArchitectureMap
    from ..resolvers import ShapeResolverCatalog


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


class ShapeReportCollector:
    def __init__(
        self,
        config: ShapeConfig,
        catalog: "ShapeResolverCatalog",
    ):
        self.config = config
        self.catalog = catalog

    def collect(self, architecture_map: "ArchitectureMap") -> ShapeReport:
        resolver_names = self.catalog.names()
        violations: list[ShapeViolation] = []
        for resolver_name in resolver_names:
            resolver = self.catalog.resolver(resolver_name)
            for source_file in architecture_map.code_map.source_files().all():
                violations.extend(
                    resolver.resolve(
                        source_file.source_id,
                        source_file.file,
                        self.config,
                    )
                )
        return ShapeReport(
            violations=tuple(violations),
            resolvers=resolver_names,
        )
