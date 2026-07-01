from abc import ABC, abstractmethod

from modwire_extraction.code import QueryableCodeMap
from pydantic import BaseModel, ConfigDict

from ..config import ArchitectureConfig
from .matching import TagMatcher
from .base import FlowAnalysisContext, FlowViolation


class FlowPipelineStepInterface(ABC):
    @abstractmethod
    def run( self, code_map: QueryableCodeMap, config: ArchitectureConfig) -> FlowReport:
        raise NotImplementedError


class FlowReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowPipelineStep(FlowPipelineStepInterface):
    def run( self, code_map: QueryableCodeMap, config: ArchitectureConfig) -> FlowReport:
        matcher = TagMatcher(config)
        violations: list[FlowViolation] = []
        analyzer_names = config.boundaries.flow.analyzers
        for analyzer_name in analyzer_names:
            analyzer = self.catalog.analyzer(analyzer_name)
            for realm in flow_realms(config.boundaries.flow):
                violations.extend(
                    analyzer.analyze(
                        FlowAnalysisContext(
                            code_map=code_map,
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
