from pydantic import BaseModel, ConfigDict

from ...boundaries import ArchitectureMap
from modwire_extraction.code import QueryableCodeMap

from ..base import InsightReporter


class UnusedExport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_id: str
    name: str
    kind: str
    crossing_type: str
    reason: str


class UnusedExportInsight(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    unused_exports: tuple[UnusedExport, ...] = ()


class ExportsReporter(InsightReporter):
    def collect(self, architecture_map: ArchitectureMap) -> None:
        ...
