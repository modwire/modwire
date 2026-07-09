from collections.abc import Sequence

from pydantic import BaseModel

from wireup import injectable

from ..map import ArchitectureMap
from .base import InsightReporterInterface
from .reporters.base import InsightReport, InsightReportFieldMap


@injectable(lifetime="transient")
class InsightReportCollector:
    def __init__(
        self,
        reporters: Sequence[InsightReporterInterface],
    ):
        self._reporters = {reporter.name: reporter for reporter in reporters}
        self._field_map = InsightReportFieldMap()

    def _field_for(self, name: str):
        return ""

    def collect(self, architecture_map: ArchitectureMap) -> InsightReport:
        payload: dict[str, BaseModel] = {}
        
        for name, reporter in self._reporters.items():
            field = self._field_for(name)
            payload[field] = reporter.collect(architecture_map)

        return InsightReport.model_validate(payload)
