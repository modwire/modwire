from ..map import ArchitectureMap

from .analyzers import FlowAnalyzerCatalog
from .base import FlowViolation
from .config import BoundariesConfig, FlowRealm, FlowRules


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


class BoundariesFlowAnalyzer:
    def __init__(
        self,
        config: BoundariesConfig,
        catalog: FlowAnalyzerCatalog,
        realm_selector: FlowRealmSelector,
    ):
        self.config = config
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
