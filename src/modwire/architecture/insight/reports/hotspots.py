from pydantic import BaseModel, ConfigDict

from ...config import ArchitectureMap
from modwire_extraction.code import QueryableCodeMap

from ..base import InsightReporter


class DependencyHotspot(BaseModel):
    source_id: str
    incoming_count: int
    outgoing_count: int
    pressure_score: int


class HotspotsReporter(InsightReporter):
    def collect(self, architecture_map: ArchitectureMap, code_map: QueryableCodeMap) -> None:
        ...