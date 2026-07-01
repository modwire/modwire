from pydantic import BaseModel

from ...boundaries.map import ArchitectureMap

from ..base import InsightReporter


class DependencyHotspot(BaseModel):
    source_id: str
    incoming_count: int
    outgoing_count: int
    pressure_score: int


class HotspotsReporter(InsightReporter):
    def collect(self, architecture_map: ArchitectureMap) -> None:
        ...
