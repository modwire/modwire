from __future__ import annotations

from ..extraction import CodeMap
from .config import ShapeConfig, validate_shape_config
from .rules import DEFAULT_SHAPE_RULES, ShapeRule
from .violations import ShapeViolation


class ShapePolicyEvaluator:
    def __init__(self, rules: tuple[ShapeRule, ...] = DEFAULT_SHAPE_RULES):
        self.rules = rules

    def evaluate(
        self,
        code_map: CodeMap,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        return evaluate_shape(code_map, config, rules=self.rules)


def evaluate_shape(
    code_map: CodeMap,
    config: ShapeConfig,
    *,
    rules: tuple[ShapeRule, ...] = DEFAULT_SHAPE_RULES,
) -> tuple[ShapeViolation, ...]:
    config = validate_shape_config(config)
    violations: list[ShapeViolation] = []
    for source_id, source_file in code_map.extraction_result.files.items():
        for rule in rules:
            violations.extend(rule.evaluate(source_id, source_file, config))
    return tuple(violations)
