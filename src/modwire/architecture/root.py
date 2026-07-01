from modwire_extraction.code import QueryableCodeMap

from .boundaries.map import ArchitectureMap, ArchitectureMapLoader
from .config import ArchitectureConfig


class ArchitectureRoot:
    config: ArchitectureConfig

    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def load_map(self, code_map: QueryableCodeMap) -> ArchitectureMap:
        return ArchitectureMapLoader(self.config).load(code_map)
