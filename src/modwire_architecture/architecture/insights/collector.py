from collections.abc import Sequence

from modwire_architecture.shared import report

from ..map.base import ArchitectureMap

from .base import InsightReporterInterface
from .reporters import InsightReport, InsightReportFieldMap


class InsightReportCollector(report.ReportCollector[InsightReport]):
    report_type: type[InsightReport] = InsightReport

    def __init__(
        self,
        reporters: Sequence[InsightReporterInterface],
    ):
        self._reporters = {reporter.name: reporter for reporter in reporters}
        self._field_map = InsightReportFieldMap()

    def _field_for(self, name: str):
        return self._field_map.field_for(name)

    def collect(self, architecture_map: ArchitectureMap) -> InsightReport:
        payload: dict[str, report.ReportItem] = {}

        for name, reporter in self._reporters.items():
            field = self._field_for(name)
            payload[field] = reporter.collect(architecture_map)

        return self.report_type.model_validate(payload)
