from collections.abc import Sequence
from modwire.shared.config import ArchitectureConfig, FlowRules

from ..map.base import ArchitectureMap, ArchitectureRealm

from .base import FlowAnalyzerInterface, FlowViolation


class BoundariesFlowAnalyzer:
    def __init__(
        self,
        config: ArchitectureConfig,
        analyzers: Sequence[FlowAnalyzerInterface],
    ):
        self.config = config.boundaries
        self._analyzers = {analyzer.name: analyzer for analyzer in analyzers}

    def analyzer_names(self) -> tuple[str, ...]:
        configured = self.config.flow.analyzers or tuple(sorted(self._analyzers))
        if self.config.rules and "module-boundaries" not in configured:
            return ("module-boundaries", *configured)
        return configured

    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        violations: list[FlowViolation] = []

        for analyzer_name in self.analyzer_names():
            analyzer = self.analyzer(analyzer_name)
            for realm in self.realms(self.config.flow):
                violations.extend(analyzer.analyze(architecture_map.with_realm(realm)))
        unique = {violation.violation_key(): violation for violation in violations}
        return tuple(unique[key] for key in sorted(unique))

    def analyzer(self, name: str) -> FlowAnalyzerInterface:
        try:
            return self._analyzers[name]
        except KeyError as error:
            known = ", ".join(sorted(self._analyzers))
            raise ValueError(
                f"Unknown flow analyzer {name!r}. Known analyzers: {known}"
            ) from error

    def realms(self, flow: FlowRules) -> tuple[ArchitectureRealm, ...]:
        if flow.realms:
            return tuple(
                ArchitectureRealm(
                    name=realm.name,
                    module_tag=realm.module_tag or flow.module_tag,
                    layers=realm.layers or flow.layers,
                )
                for realm in flow.realms
            )

        return (
            ArchitectureRealm(
                name="",
                module_tag=flow.module_tag,
                layers=flow.layers,
            ),
        )
