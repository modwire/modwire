from pydantic import BaseModel


class EdgeRuleViolation(BaseModel):
    source_id: str
    target_id: str
    source_pattern: str
    target_pattern: str
    rule_name: str


class FlowViolation(BaseModel):
    violation_type: str
    path: tuple[str, ...]
    violation_index: int
    rule_name: str
    message: str
