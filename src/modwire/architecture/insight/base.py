import abc

from ..boundaries import ArchitectureMap


class InsightReporter(abc.ABC):
    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> None:
        raise NotImplementedError
