from pydantic import BaseModel, ConfigDict

from ...config import ArchitectureMap
from modwire_extraction.code import QueryableCodeMap

from ..base import InsightReporter


class ArchitectureCluster(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str
    files: tuple[str, ...]
    incoming_count: int
    outgoing_count: int
    pressure_score: int
    top_files: tuple[str, ...]


class ClustersReporter(InsightReporter):
    def collect(self, architecture_map: ArchitectureMap, code_map: QueryableCodeMap) -> None:
        ...