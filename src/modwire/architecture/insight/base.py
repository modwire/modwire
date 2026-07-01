import abc

from pydantic import BaseModel

from ..boundaries.map import ArchitectureMap


class InsightReporter(BaseModel, abc.ABC):
    name: str
    title: str

    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> BaseModel:
        raise NotImplementedError
