import abc

from pydantic import BaseModel

from ..map import ArchitectureMap


class InsightReporterInterface(abc.ABC):
    name: str
    title: str

    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> BaseModel:
        raise NotImplementedError
