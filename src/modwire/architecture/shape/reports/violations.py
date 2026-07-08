from ...map.map import ArchitectureMap
from ...base import ReportCategory, ReportItem
from ..base import ShapeViolation
from ..config import ShapeConfig
from ..resolvers import ShapeResolverCatalog


class ShapeReport(ReportItem):
    report_id: str = "architecture.violations.shape"
    report_title: str = "Shape Violations"
    report_category: ReportCategory = ReportCategory.SHAPE
    report_path: str = "violations.shape"
    report_order: int = 20

    violations: tuple[ShapeViolation, ...] = ()
    resolvers: tuple[str, ...] = ()


class ShapeReportCollector:
    def __init__(
        self,
        config: ShapeConfig,
        catalog: ShapeResolverCatalog,
    ):
        self.config = config
        self.catalog = catalog

    def collect(self, architecture_map: ArchitectureMap) -> ShapeReport:
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
