from __future__ import annotations

import json
from dataclasses import asdict
from typing import Callable

from .analyzers import analyzer_title
from .violations import EDGE_RULE_TYPE, EdgeRuleViolation, FlowViolation

GROUP_TITLES = {
    EDGE_RULE_TYPE: "Edge Rule Violations",
}

PathDisplay = Callable[[str], str]


def summary(report) -> str:
    return "\n".join(
        (
            "Boundaries Summary:",
            f"- Paths found in scope: {report.files_found}",
            f"- Paths excluded by rules: {report.files_excluded}",
            f"- Files checked: {report.files_checked}",
        )
    )


def violations(report) -> str:
    return render_violations(report.violations)


def render_violations(
    violations: tuple[EdgeRuleViolation | FlowViolation, ...],
    *,
    path_display: PathDisplay = str,
) -> str:
    groups: dict[str, list[str]] = {}
    for violation in violations:
        violation_type = _type(violation)
        title = GROUP_TITLES.get(violation_type)
        if title is None:
            title = analyzer_title(violation_type)
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
        violation_type = _type(violation)
        title = GROUP_TITLES.get(violation_type)
        if title is None:
            title = analyzer_title(violation_type)
        groups.setdefault(title, []).append(violation_to_dict(violation))
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
    path[violation.violation_index] = f"[{path[violation.violation_index]}]"
    return f"{' -> '.join(path)}  {violation.violation_type}"


def render_json(report) -> str:
    return json.dumps(
        {
            "project_root": str(report.project_root),
            "config_path": str(report.config_path),
            "config_format": report.config_format,
            "language": report.language,
            "runtime_command": report.runtime_command,
            "files_found": report.files_found,
            "files_excluded": report.files_excluded,
            "files_checked": report.files_checked,
            "violations": [_json_violation(v) for v in report.violations],
        },
        indent=2,
        sort_keys=True,
    )


def render_dot(report) -> str:
    edges = dict.fromkeys(edge for violation in report.violations for edge in _edges(violation))
    return "\n".join(
        ("digraph architecture_violations {", "  rankdir=LR;")
        + tuple(f'  "{source}" -> "{target}";' for source, target in edges)
        + ("}",)
    )


def _json_violation(violation):
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


def _edges(violation):
    if isinstance(violation, EdgeRuleViolation):
        return ((violation.source_id, violation.target_id),)
    return tuple(zip(violation.path, violation.path[1:], strict=False))


def _type(violation):
    return EDGE_RULE_TYPE if isinstance(violation, EdgeRuleViolation) else violation.violation_type


def violation_to_dict(violation: EdgeRuleViolation | FlowViolation) -> dict[str, object]:
    payload = asdict(violation)
    payload["type"] = _type(violation)
    payload["path"] = (
        [violation.source_id, violation.target_id]
        if isinstance(violation, EdgeRuleViolation)
        else list(violation.path)
    )
    if isinstance(violation, EdgeRuleViolation):
        payload["violation_index"] = 1
    return payload
