from __future__ import annotations

from typing import Callable

from .analyzers import analyzer_title
from .violations import EDGE_RULE_TYPE, EdgeRuleViolation, FlowViolation, violation_to_dict

GROUP_TITLES = {
    EDGE_RULE_TYPE: "Edge Rule Violations",
}

PathDisplay = Callable[[str], str]


def render_violations(
    violations: tuple[EdgeRuleViolation | FlowViolation, ...],
    *,
    path_display: PathDisplay = str,
) -> str:
    groups: dict[str, list[str]] = {}
    for violation in violations:
        title = _title(violation)
        groups.setdefault(title, []).append(compact(violation, path_display=path_display))
    return "\n".join(
        line
        for title, entries in groups.items()
        for line in (f"{title}:", *(f"- {entry}" for entry in entries))
    )


def structured_groups(
    violations: tuple[EdgeRuleViolation | FlowViolation, ...],
) -> tuple[dict[str, object], ...]:
    groups: dict[str, list[dict[str, object]]] = {}
    for violation in violations:
        title = _title(violation)
        groups.setdefault(title, []).append(render_violation_payload(violation))
    return tuple(
        {
            "title": title,
            "violations": entries,
        }
        for title, entries in groups.items()
    )


def compact(
    violation: EdgeRuleViolation | FlowViolation,
    *,
    path_display: PathDisplay = str,
) -> str:
    if isinstance(violation, EdgeRuleViolation):
        return (
            f"{path_display(violation.source_id)} -> [{path_display(violation.target_id)}] "
            f"blocked by {violation.source_pattern} -> {violation.target_pattern}"
        )
    path = list(violation.path)
    path = [path_display(entry) for entry in path]
    if path:
        index = min(max(violation.violation_index, 0), len(path) - 1)
        path[index] = f"[{path[index]}]"
    return f"{' -> '.join(path)}  {violation.violation_type}"


def render_violation_payload(
    violation: EdgeRuleViolation | FlowViolation,
) -> dict[str, object]:
    payload = violation_to_dict(violation)
    payload["type"] = _type(violation)
    payload["path"] = (
        [violation.source_id, violation.target_id]
        if isinstance(violation, EdgeRuleViolation)
        else list(violation.path)
    )
    if isinstance(violation, EdgeRuleViolation):
        payload["violation_index"] = 1
    return payload


def _type(violation):
    return EDGE_RULE_TYPE if isinstance(violation, EdgeRuleViolation) else violation.violation_type


def _title(violation: EdgeRuleViolation | FlowViolation) -> str:
    violation_type = _type(violation)
    if violation_type in GROUP_TITLES:
        return GROUP_TITLES[violation_type]
    try:
        return analyzer_title(violation_type)
    except KeyError:
        return f"{violation_type.replace('-', ' ').title()} Violations"


__all__ = [
    "compact",
    "render_violation_payload",
    "render_violations",
    "structured_groups",
]
