from pydantic import BaseModel, ConfigDict

from ...config import ArchitectureMap
from modwire_extraction.code import QueryableCodeMap

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
    def collect(self, architecture_map: ArchitectureMap, code_map: QueryableCodeMap) -> None:
        ...