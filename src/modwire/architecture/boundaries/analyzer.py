from typing import Annotated

from wireup import Inject, injectable

from modwire.shared.config import ArchitectureConfig, FlowRules, FlowRealm

from ..map.map import ArchitectureMap

from .analyzers import FlowAnalyzerCatalog
from .base import FlowViolation


@injectable
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


@injectable(lifetime="transient")
class BoundariesFlowAnalyzer:
    def __init__(
        self,
        config: Annotated[ ArchitectureConfig, Inject(config="architecture") ],
        catalog: FlowAnalyzerCatalog,
        realm_selector: FlowRealmSelector,
    ):
        self.config = config.boundaries
        self.catalog = catalog
        self.realm_selector = realm_selector

    def analyzer_names(self) -> tuple[str, ...]:
        return self.config.flow.analyzers or self.catalog.names()

    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        violations: list[FlowViolation] = []

        for analyzer_name in self.analyzer_names():
            analyzer = self.catalog.analyzer(analyzer_name)
            for realm in self.realm_selector.select(self.config.flow):
                violations.extend(analyzer.analyze(architecture_map.with_realm(realm)))
        return tuple(violations)
