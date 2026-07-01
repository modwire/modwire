import abc

from ...map import ArchitectureMap


class InsightReporter(abc.ABC):
    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> None:
        raise NotImplementedError
