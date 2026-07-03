from abc import ABC, abstractmethod

from modwire.shared import ModwireBaseModel

from .map import ArchitectureMap


EDGE_RULE_TYPE = "edge-rule"


class EdgeRuleViolation(ModwireBaseModel):
    source_id: str
    target_id: str
    source_pattern: str
    target_pattern: str
    rule_name: str


class FlowViolation(ModwireBaseModel):
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


class FlowAnalyzerInterface(ABC):
    @abstractmethod
    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        raise NotImplementedError


class FlowAnalyzer(FlowAnalyzerInterface):
    name: str
    title: str

    @abstractmethod
    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        raise NotImplementedError

    def rule_name(self, architecture_map: ArchitectureMap) -> str:
        if architecture_map.realm.name:
            return f"analyzer:{architecture_map.realm.name}:{self.name}"
        return f"analyzer:{self.name}"

    def module_for(self, architecture_map: ArchitectureMap, source_id: str) -> str:
        module_tag = architecture_map.realm.module_tag
        if not module_tag:
            return ""

        match = architecture_map.tag_map.first_match(source_id, (module_tag,))
        if match is None:
            return ""
        return match.captured_path or match.name

    def layer_for(
        self,
        architecture_map: ArchitectureMap,
        source_id: str,
        layers: tuple[str, ...] | None = None,
    ) -> str:
        layer_names = layers or architecture_map.realm.layers
        if not layer_names:
            return ""

        match = architecture_map.tag_map.first_match(source_id, layer_names)
        if match is None:
            return ""
        return match.name

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
