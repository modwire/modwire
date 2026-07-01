import abc

from modwire_extraction.code import QueryableCodeMap

from ..config import ArchitectureMap


class InsightReporter(abc.ABC):
    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap, code_map: QueryableCodeMap) -> None:
        raise NotImplementedError
