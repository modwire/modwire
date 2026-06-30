from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from modwire_extraction import ModwireExtraction


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
