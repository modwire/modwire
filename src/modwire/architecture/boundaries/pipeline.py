from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from .base import FlowViolation
from .config import FlowRealm, FlowRules
from .map import ArchitectureMap
from .analyzers.backward import BackwardFlowAnalyzer
from .analyzers.no_cycles import NoCyclesFlowAnalyzer
from .analyzers.no_reentry import NoReentryFlowAnalyzer


class FlowReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowPipelineStepInterface(ABC):
    @abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> FlowReport:
        raise NotImplementedError


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

    def analyzer(self, name: str):
        try:
            return self._analyzers[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._analyzers))
            raise ValueError(f"Unknown flow analyzer {name!r}. Known analyzers: {known}") from exc


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


class FlowPipelineStep(FlowPipelineStepInterface):
    def __init__(
        self,
        catalog: FlowAnalyzerCatalog | None = None,
        realm_selector: FlowRealmSelector | None = None,
    ):
        self.catalog = catalog or FlowAnalyzerCatalog()
        self.realm_selector = realm_selector or FlowRealmSelector()

    def run(self, architecture_map: ArchitectureMap) -> FlowReport:
        violations: list[FlowViolation] = []
        flow = architecture_map.config.boundaries.flow
        analyzer_names = flow.analyzers
        for analyzer_name in analyzer_names:
            analyzer = self.catalog.analyzer(analyzer_name)
            for realm in self.realm_selector.select(flow):
                violations.extend(analyzer.analyze(architecture_map.with_realm(realm)))
        return FlowReport(
            violations=tuple(violations),
            analyzers=analyzer_names,
        )


__all__ = [
    "FlowAnalyzerCatalog",
    "FlowRealmSelector",
    "FlowPipelineStep",
    "FlowPipelineStepInterface",
    "FlowReport",
]
