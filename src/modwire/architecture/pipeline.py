from __future__ import annotations

from modwire_extraction.code import QueryableCodeMap
from pydantic import BaseModel, ConfigDict, Field

from .flow import FlowPipelineStep, FlowReport
from .map import ArchitectureConfig


class ArchitecturePipelineResult(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    flow: FlowReport


class ArchitecturePipeline(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    flow_step: FlowPipelineStep = Field(default_factory=FlowPipelineStep)

    def run(
        self,
        code_map: QueryableCodeMap,
        config: ArchitectureConfig,
    ) -> ArchitecturePipelineResult:
        flow = self.flow_step.run(code_map, config)
        return ArchitecturePipelineResult(flow=flow)


__all__ = [
    "ArchitecturePipeline",
    "ArchitecturePipelineResult",
]
