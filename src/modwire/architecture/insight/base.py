import abc

from ..boundaries.map import ArchitectureMap


class InsightReporter(abc.ABC):
    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> None:
        raise NotImplementedError
