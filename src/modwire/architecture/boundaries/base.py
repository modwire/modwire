from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from .map import ArchitectureMap


EDGE_RULE_TYPE = "edge-rule"


class EdgeRuleViolation(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_id: str
    target_id: str
    source_pattern: str
    target_pattern: str
    rule_name: str


class FlowViolation(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    violation_type: str
    path: tuple[str, ...]
    violation_index: int
    rule_name: str
    message: str


class FlowAnalyzerInterface(ABC):
    @abstractmethod
    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        raise NotImplementedError


class FlowAnalyzer(BaseModel, FlowAnalyzerInterface):
    name: str
    title: str

    @abstractmethod
    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        raise NotImplementedError

    def rule_name(self, architecture_map: ArchitectureMap) -> str:
        if architecture_map.config.realm.name:
            return f"analyzer:{architecture_map.config.realm.name}:{self.name}"
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
