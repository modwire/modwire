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
    def collect(self, architecture_map: ArchitectureMap) -> None:
        ...
