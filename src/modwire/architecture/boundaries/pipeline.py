from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from .map import ArchitectureMap
from .base import FlowViolation


class FlowReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowPipelineStepInterface(ABC):
    @abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> FlowReport:
        raise NotImplementedError


class FlowPipelineStep(FlowPipelineStepInterface):
    def run(self, architecture_map: ArchitectureMap) -> FlowReport:
        violations: list[FlowViolation] = []
        analyzer_names = config.boundaries.flow.analyzers
        for analyzer_name in analyzer_names:
            analyzer = self.catalog.analyzer(analyzer_name)
            for realm in flow_realms(config.boundaries.flow):
                violations.extend(
                    analyzer.analyze(
                        FlowContext(
                            tags=matcher,
                            realm=realm,
                            config=config,
                        )
                    )
                )
        return FlowReport(
            violations=tuple(violations),
            analyzers=analyzer_names,
        )


__all__ = [
    "FlowPipelineStep",
    "FlowPipelineStepInterface",
    "FlowReport",
]
