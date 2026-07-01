from .config import ArchitectureConfig, ArchitectureMap


class ArchitectureRoot:
    config: ArchitectureConfig

    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def load_map(self) -> "ArchitectureMap":

        return ArchitectureMap.load(self.config.root)

