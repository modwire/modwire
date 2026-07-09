from collections.abc import Sequence
from typing import Annotated

from wireup import Inject, injectable

from modwire.shared import report
from modwire.shared.config import ArchitectureConfig

from ..map import ArchitectureMap
from .base import ShapeResolverInterface, ShapeViolation


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
        resolvers: Sequence[ShapeResolverInterface],
    ):
        self.config = config.shape
        self.resolvers = tuple(sorted(resolvers, key=lambda resolver: resolver.name))

    def collect(self, architecture_map: ArchitectureMap) -> ShapeReport:
        resolver_names = tuple(resolver.name for resolver in self.resolvers)
        violations: list[ShapeViolation] = []
        for resolver in self.resolvers:
            violations.extend(resolver.resolve(architecture_map, self.config))
        return ShapeReport(
            violations=tuple(violations),
            resolvers=resolver_names,
        )
