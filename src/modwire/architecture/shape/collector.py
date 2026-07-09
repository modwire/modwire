from typing import Annotated

from wireup import Inject, injectable

from modwire.shared import report
from modwire.shared.config import ArchitectureConfig

from ..map import ArchitectureMap
from .base import ShapeViolation


class ShapeReport(report.ReportItem):
    report_id: str = "architecture.violations.shape"
    report_title: str = "Shape Violations"
    report_path: str = "violations.shape"
    report_order: int = 20

    violations: tuple[ShapeViolation, ...] = ()
    resolvers: tuple[str, ...] = ()


@injectable(lifetime="transient")
class ShapeReportCollector:
    def __init__(
        self,
        config: Annotated[ArchitectureConfig, Inject(config="architecture")],
    ):
        self.config = config.shape

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
