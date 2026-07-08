import abc

from pydantic import BaseModel

from ...map.map import ArchitectureMap


class InsightReporter(abc.ABC):
    name: str
    title: str

    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> BaseModel:
        raise NotImplementedError
