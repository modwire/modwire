from __future__ import annotations

from abc import ABC, abstractmethod

from modwire_extraction.code import QueryableCodeMap
from pydantic import BaseModel, ConfigDict, Field

from ..map import ArchitectureConfig, flow_realms
from ..matching import TagMatcher
from .base import FlowAnalysisContext, FlowViolation
from .catalog import FlowAnalyzerCatalog


class FlowPipelineStepInterface(ABC):
    @abstractmethod
    def run(
        self,
        code_map: QueryableCodeMap,
        config: ArchitectureConfig,
    ) -> FlowReport:
        raise NotImplementedError


class FlowReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowPipelineStep(BaseModel, FlowPipelineStepInterface):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    catalog: FlowAnalyzerCatalog = Field(default_factory=FlowAnalyzerCatalog)

    def run(
        self,
        code_map: QueryableCodeMap,
        config: ArchitectureConfig,
    ) -> FlowReport:
        matcher = TagMatcher(config)
        violations: list[FlowViolation] = []
        analyzer_names = config.rules.flow.analyzers
        for analyzer_name in analyzer_names:
            analyzer = self.catalog.analyzer(analyzer_name)
            for realm in flow_realms(config.rules.flow):
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
