from pydantic import BaseModel, ConfigDict

from ...config import ArchitectureMap
from modwire_extraction.code import QueryableCodeMap

from ..base import InsightReporter


class CoherenceSummary(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    roots: tuple[str, ...]
    leaves: tuple[str, ...]
    isolated: tuple[str, ...]
    external_dependencies: tuple[str, ...]


class CoherenceReporter(InsightReporter):
    def collect(self, architecture_map: ArchitectureMap, code_map: QueryableCodeMap) -> None:
        ...