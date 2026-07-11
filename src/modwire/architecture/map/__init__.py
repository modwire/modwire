from modwire.shared.config import ArchitectureConfig


def standard_map_components(config: ArchitectureConfig):
    from .collector import MapReportCollector
    from .loader import ArchitectureMapLoader

    return ArchitectureMapLoader(config), MapReportCollector()


__all__ = ["standard_map_components"]
