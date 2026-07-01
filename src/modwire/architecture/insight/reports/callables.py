from pydantic import BaseModel, ConfigDict

from ...boundaries.map import ArchitectureMap
from ..base import InsightReporter


class CallableReportEntry(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_callable: str
    calls: tuple[str, ...]
    callers: tuple[str, ...]


class CallableReport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    entries: tuple[CallableReportEntry, ...] = ()


class CallablesReporter(InsightReporter):
    name: str = "callables"
    title: str = "Callable Graph"

    def collect(self, architecture_map: ArchitectureMap) -> CallableReport:
        calls_by_source: dict[str, list[str]] = {}
        callers_by_target: dict[str, list[str]] = {}

        for call_result in architecture_map.code_map.calls().all():
            call = call_result.item
            target = call.target_callable_id or call.expression
            calls_by_source.setdefault(call.source_callable_id, []).append(target)
            if call.target_callable_id:
                callers_by_target.setdefault(call.target_callable_id, []).append(
                    call.source_callable_id
                )

        entries = tuple(
            CallableReportEntry(
                source_callable=callable_result.item.id,
                calls=tuple(sorted(set(calls_by_source.get(callable_result.item.id, ())))),
                callers=tuple(
                    sorted(set(callers_by_target.get(callable_result.item.id, ())))
                ),
            )
            for callable_result in sorted(
                architecture_map.code_map.callables().all(),
                key=lambda result: result.item.id,
            )
        )
        return CallableReport(entries=entries)


__all__ = ["CallableReport", "CallableReportEntry", "CallablesReporter"]
