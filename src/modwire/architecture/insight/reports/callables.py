from typing import ClassVar

from modwire.architecture.report import ReportCategory, ReportItem
from modwire.shared import ModwireBaseModel

from ...boundaries.map import ArchitectureMap
from ..base import InsightReporter


class CallableReportEntry(ModwireBaseModel):
    source_callable: str
    calls: tuple[str, ...]
    callers: tuple[str, ...]


class CallablesReport(ReportItem):
    report_id: ClassVar[str] = "architecture.insights.callables"
    report_title: ClassVar[str] = "Callable Graph"
    report_category: ClassVar[ReportCategory] = ReportCategory.INSIGHT
    report_path: ClassVar[str] = "insights.callables"
    report_order: ClassVar[int] = 40

    entries: tuple[CallableReportEntry, ...] = ()


class CallablesReporter(InsightReporter):
    name: str = "callables"
    title: str = "Callable Graph"

    def collect(self, architecture_map: ArchitectureMap) -> CallablesReport:
        calls_by_source: dict[str, list[str]] = {}
        callers_by_target: dict[str, list[str]] = {}

        for call_result in architecture_map.code_map.calls().all():
            call = call_result.item
            target = call.target_callable_id or call.expression
            calls_by_source.setdefault(
                call.source_callable_id, []).append(target)
            if call.target_callable_id:
                callers_by_target.setdefault(call.target_callable_id, []).append(
                    call.source_callable_id
                )

        entries = tuple(
            CallableReportEntry(
                source_callable=callable_result.item.id,
                calls=tuple(
                    sorted(set(calls_by_source.get(callable_result.item.id, ())))),
                callers=tuple(
                    sorted(set(callers_by_target.get(
                        callable_result.item.id, ())))
                ),
            )
            for callable_result in sorted(
                architecture_map.code_map.callables().all(),
                key=lambda result: result.item.id,
            )
        )
        return CallablesReport(entries=entries)
