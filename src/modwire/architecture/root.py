from ..architecture.boundaries import ArchitectureMap, load_architecture_map

from .config import ArchitectureConfig


class ArchitectureRoot:
    config: ArchitectureConfig

    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def load_map(self) -> ArchitectureMap:
        return load_architecture_map(self.config)


