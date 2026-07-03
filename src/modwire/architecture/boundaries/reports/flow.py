from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from ...report import ReportCategory, ReportItem
from ..analyzers import (
    BackwardFlowAnalyzer,
    NoCyclesFlowAnalyzer,
    NoReentryFlowAnalyzer,
)
from ..base import FlowAnalyzer, FlowViolation
from ..config import FlowRealm, FlowRules


if TYPE_CHECKING:
    from ..map import ArchitectureMap


class FlowReport(ReportItem):
    report_id: ClassVar[str] = "architecture.violations.flow"
    report_title: ClassVar[str] = "Dependency Flow"
    report_category: ClassVar[ReportCategory] = ReportCategory.FLOW
    report_path: ClassVar[str] = "violations.flow"
    report_order: ClassVar[int] = 10

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowRealmSelector:
    def select(self, flow: FlowRules) -> tuple[FlowRealm, ...]:
        if flow.realms:
            return tuple(
                FlowRealm(
                    name=realm.name,
                    module_tag=realm.module_tag or flow.module_tag,
                    layers=realm.layers or flow.layers,
                )
                for realm in flow.realms
            )
        return (
            FlowRealm(
                module_tag=flow.module_tag,
                layers=flow.layers,
            ),
        )


class FlowAnalyzerCatalog:
    def __init__(self):
        self._analyzers = {
            analyzer.name: analyzer
            for analyzer in (
                BackwardFlowAnalyzer(),
                NoCyclesFlowAnalyzer(),
                NoReentryFlowAnalyzer(),
            )
        }

    def analyzer(self, name: str) -> FlowAnalyzer:
        try:
            return self._analyzers[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._analyzers))
            raise ValueError(
                f"Unknown flow analyzer {name!r}. Known analyzers: {known}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._analyzers)


class FlowReportCollector:
    def __init__(
        self,
        catalog: FlowAnalyzerCatalog | None = None,
        realm_selector: FlowRealmSelector | None = None,
    ):
        self.catalog = catalog or FlowAnalyzerCatalog()
        self.realm_selector = realm_selector or FlowRealmSelector()

    def collect_all(self, architecture_map: ArchitectureMap) -> FlowReport:
        return self.collect(architecture_map, self.catalog.names())

    def collect(
        self,
        architecture_map: ArchitectureMap,
        analyzer_names: tuple[str, ...],
    ) -> FlowReport:
        violations: list[FlowViolation] = []
        flow = architecture_map.config.boundaries.flow
        for analyzer_name in analyzer_names:
            analyzer = self.catalog.analyzer(analyzer_name)
            for realm in self.realm_selector.select(flow):
                violations.extend(analyzer.analyze(architecture_map.with_realm(realm)))
        return FlowReport(
            violations=tuple(violations),
            analyzers=analyzer_names,
        )
