from abc import ABC, abstractmethod

from ..base import FlowViolation
from ..map import ArchitectureMap
from ..reports import FlowRealmSelector, FlowReport

from .catalog import FlowAnalyzerCatalog


class FlowPipelineStepInterface(ABC):
    @abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> FlowReport:
        raise NotImplementedError


class FlowPipelineStep(FlowPipelineStepInterface):
    def __init__(
        self,
    ):
        self.catalog = FlowAnalyzerCatalog()
        self.realm_selector = FlowRealmSelector()

    def run(self, architecture_map: ArchitectureMap) -> FlowReport:
        return self.run_analyzers(
            architecture_map,
            architecture_map.config.boundaries.flow.analyzers,
        )

    def run_all(self, architecture_map: ArchitectureMap) -> FlowReport:
        return self.run_analyzers(architecture_map, self.catalog.names())

    def run_analyzers(
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
