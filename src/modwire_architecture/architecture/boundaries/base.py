from abc import ABC, abstractmethod

from modwire_architecture.shared import ModwireModel

from ..map.base import ArchitectureMap


EDGE_RULE_TYPE = "edge-rule"


class EdgeRuleViolation(ModwireModel):
    source_id: str
    target_id: str
    source_pattern: str
    target_pattern: str
    rule_name: str


class FlowViolation(ModwireModel):
    violation_type: str
    path: tuple[str, ...]
    violation_index: int
    rule_name: str
    message: str
    source_module: str = ""
    target_module: str = ""

    def violation_key(self) -> tuple[object, ...]:
        return (
            self.violation_type,
            self.path,
            self.violation_index,
            self.rule_name,
            self.message,
            self.source_module,
            self.target_module,
        )


class FlowAnalyzerInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        raise NotImplementedError

    def rule_name(self, architecture_map: ArchitectureMap) -> str:
        if architecture_map.realm.name:
            return f"analyzer:{architecture_map.realm.name}:{self.name}"
        return f"analyzer:{self.name}"
