from __future__ import annotations

from dataclasses import dataclass


EDGE_RULE_TYPE = "edge-rule"


@dataclass(frozen=True)
class EdgeRuleViolation:
    source_id: str
    target_id: str
    source_pattern: str
    target_pattern: str
    rule_name: str

    def to_dict(self) -> dict[str, str]:
        return {
            "violation_type": EDGE_RULE_TYPE,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "source_pattern": self.source_pattern,
            "target_pattern": self.target_pattern,
            "rule_name": self.rule_name,
        }


@dataclass(frozen=True)
class FlowViolation:
    violation_type: str
    path: tuple[str, ...]
    violation_index: int
    rule_name: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "violation_type": self.violation_type,
            "path": self.path,
            "violation_index": self.violation_index,
            "rule_name": self.rule_name,
            "message": self.message,
        }


def violation_to_dict(violation: EdgeRuleViolation | FlowViolation) -> dict[str, object]:
    return violation.to_dict()
