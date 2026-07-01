from __future__ import annotations

from abc import ABC, abstractmethod

from modwire_extraction.code import QueryableCodeMap
from pydantic import BaseModel, ConfigDict, computed_field

from ..map import ArchitectureConfig, ArchitectureFlowRealm
from ..matching import TagMatcher


EDGE_RULE_TYPE = "edge-rule"


class ViolationInterface(ABC):
    @abstractmethod
    def violation_key(self) -> tuple[object, ...]:
        raise NotImplementedError


class FlowAnalysisContext(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    code_map: QueryableCodeMap
    tags: TagMatcher
    realm: ArchitectureFlowRealm
    config: ArchitectureConfig


class FlowAnalyzerInterface(ABC):
    @abstractmethod
    def analyze(self, context: FlowAnalysisContext) -> tuple[FlowViolation, ...]:
        raise NotImplementedError


class FlowAnalyzer(BaseModel, FlowAnalyzerInterface):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    title: str

    @abstractmethod
    def analyze(self, context: FlowAnalysisContext) -> tuple[FlowViolation, ...]:
        raise NotImplementedError

    def rule_name(self, context: FlowAnalysisContext) -> str:
        if context.realm.name:
            return f"analyzer:{context.realm.name}:{self.name}"
        return f"analyzer:{self.name}"

    def dedupe(self, violations: list[FlowViolation]) -> tuple[FlowViolation, ...]:
        seen: set[tuple[object, ...]] = set()
        result: list[FlowViolation] = []
        for violation in violations:
            key = violation.violation_key()
            if key in seen:
                continue
            seen.add(key)
            result.append(violation)
        return tuple(result)

    def module_for(self, context: FlowAnalysisContext, source_id: str) -> str:
        if not context.realm.module_tag:
            return ""
        match = context.tags.match(source_id, context.realm.module_tag)
        if match is None:
            return ""
        return match.captured_path

    def layer_for(
        self,
        context: FlowAnalysisContext,
        source_id: str,
        layers: tuple[str, ...],
    ) -> str:
        if not layers:
            return ""
        match = context.tags.first_match(source_id, layers)
        if match is not None:
            return match.name if match.name in layers else match.pattern
        for layer in layers:
            if context.tags.match(source_id, layer) is not None:
                return layer
        return ""


class EdgeRuleViolation(BaseModel, ViolationInterface):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_id: str
    target_id: str
    source_pattern: str
    target_pattern: str
    rule_name: str

    @computed_field
    @property
    def violation_type(self) -> str:
        return EDGE_RULE_TYPE

    def violation_key(self) -> tuple[object, ...]:
        return (
            self.violation_type,
            self.source_id,
            self.target_id,
            self.source_pattern,
            self.target_pattern,
            self.rule_name,
        )


class FlowViolation(BaseModel, ViolationInterface):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violation_type: str
    path: tuple[str, ...]
    violation_index: int
    rule_name: str
    message: str

    def violation_key(self) -> tuple[object, ...]:
        return (
            self.violation_type,
            self.path,
            self.violation_index,
            self.rule_name,
            self.message,
        )

__all__ = [
    "EDGE_RULE_TYPE",
    "EdgeRuleViolation",
    "FlowAnalysisContext",
    "FlowAnalyzer",
    "FlowAnalyzerInterface",
    "FlowViolation",
    "ViolationInterface",
]
