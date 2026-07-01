from modwire_extraction.code import QueryableCodeMap

from .boundaries import ArchitectureMap, load_architecture_map
from .config import ArchitectureConfig


class ArchitectureRoot:
    config: ArchitectureConfig

    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def load_map(self, code_map: QueryableCodeMap) -> ArchitectureMap:
        return load_architecture_map(self.config, code_map)
