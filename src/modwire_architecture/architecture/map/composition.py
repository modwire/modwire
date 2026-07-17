from modwire_architecture.shared.config import ArchitectureConfig

from .collector import MapReportCollector
from .loader import ArchitectureMapLoader


def standard_map_components(config: ArchitectureConfig):
    return ArchitectureMapLoader(config), MapReportCollector()
