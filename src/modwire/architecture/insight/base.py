import abc
from typing import TYPE_CHECKING

from pydantic import BaseModel


if TYPE_CHECKING:
    from ..boundaries import ArchitectureMap


class InsightReporter(abc.ABC):
    name: str
    title: str

    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> BaseModel:
        raise NotImplementedError
