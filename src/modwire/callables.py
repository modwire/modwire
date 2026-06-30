from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ._code_map import calls_from, calls_to, source_callables
from .definitions import SourceCall, SourceCallable


PathDisplay = Callable[[str], str]


@dataclass(frozen=True)
class CallableReportEntry:
    source_callable: SourceCallable
    calls: tuple[SourceCall, ...]
    callers: tuple[SourceCall, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "callable": self.source_callable.model_dump(mode="json"),
            "calls": [source_call.model_dump(mode="json") for source_call in self.calls],
            "callers": [
                source_call.model_dump(mode="json") for source_call in self.callers
            ],
        }


def callable_report_entries(code_map) -> tuple[CallableReportEntry, ...]:
    return tuple(
        CallableReportEntry(
            source_callable=source_callable,
            calls=tuple(
                sorted(
                    calls_from(code_map, source_callable.id),
                    key=lambda source_call: (
                        source_call.line,
                        source_call.target_name,
                        source_call.expression,
                    ),
                )
            ),
            callers=tuple(
                sorted(
                    calls_to(code_map, source_callable.id),
                    key=lambda source_call: (
                        source_call.source_id,
                        source_call.line,
                        source_call.source_callable_id,
                    ),
                )
            ),
        )
        for source_callable in sorted(
            source_callables(code_map),
            key=lambda source_callable: (
                source_callable.source_id,
                source_callable.line_start,
                source_callable.qualified_name,
            ),
        )
    )


def structured_callable_report(code_map) -> tuple[dict[str, object], ...]:
    return tuple(entry.to_dict() for entry in callable_report_entries(code_map))


def render_callable_report(
    code_map,
    *,
    path_display: PathDisplay = str,
) -> str:
    entries = callable_report_entries(code_map)
    if not entries:
        return "Callable Report\n\nNo callables found."

    callable_names = {
        entry.source_callable.id: entry.source_callable.qualified_name
        for entry in entries
    }
    lines = ["Callable Report", ""]
    current_source_id = ""
    for entry in entries:
        source_callable = entry.source_callable
        if source_callable.source_id != current_source_id:
            current_source_id = source_callable.source_id
            lines.extend([f"## {path_display(current_source_id)}", ""])
        lines.append(
            "- "
            f"{source_callable.qualified_name} "
            f"[{source_callable.kind}] "
            f"lines {source_callable.line_start}-{source_callable.line_end}"
        )
        lines.append("  Calls:")
        lines.extend(
            _call_lines(
                entry.calls,
                callable_names=callable_names,
                direction="outgoing",
                path_display=path_display,
            )
        )
        lines.append("  Called by:")
        lines.extend(
            _call_lines(
                entry.callers,
                callable_names=callable_names,
                direction="incoming",
                path_display=path_display,
            )
        )
        lines.append("")
    return "\n".join(lines).rstrip()


def _call_lines(
    calls: tuple[SourceCall, ...],
    *,
    callable_names: dict[str, str],
    direction: str,
    path_display: PathDisplay,
) -> list[str]:
    if not calls:
        return ["  - none"]

    rendered = []
    for source_call in calls:
        if direction == "incoming":
            caller_name = callable_names.get(
                source_call.source_callable_id,
                source_call.source_callable_id,
            )
            rendered.append(
                f"  - {caller_name} "
                f"at {path_display(source_call.source_id)}:{source_call.line}"
            )
            continue

        target = (
            callable_names[source_call.target_callable_id]
            if source_call.target_callable_id in callable_names
            else source_call.target_name
        )
        rendered.append(
            f"  - {source_call.expression} -> {target} "
            f"at {path_display(source_call.source_id)}:{source_call.line} "
            f"({source_call.resolution})"
        )
    return rendered


__all__ = [
    "CallableReportEntry",
    "callable_report_entries",
    "render_callable_report",
    "structured_callable_report",
]
