from __future__ import annotations

from .config import ShapeConfig, validate_shape_config
from .rules import ShapeRule
from .violations import ShapeViolation


class ShapePolicyEvaluator:
    def __init__(self, rules: tuple[ShapeRule, ...] = DEFAULT_SHAPE_RULES):
        self.rules = rules

    def evaluate(
        self,
        code_map,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        return evaluate_shape(code_map, config, rules=self.rules)


def evaluate_shape(
    code_map,
    config: ShapeConfig,
    *,
    rules: tuple[ShapeRule, ...] = DEFAULT_SHAPE_RULES,
) -> tuple[ShapeViolation, ...]:
    config = validate_shape_config(config)
    violations: list[ShapeViolation] = []
    for source_id, source_file in source_files(code_map).items():
        for rule in rules:
            violations.extend(rule.evaluate(source_id, source_file, config))
    return tuple(violations)
