from dependency_injector import containers, providers

from ..config import ArchitectureConfig
from .loader import ArchitectureMapLoader


class MapContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=ArchitectureConfig)
    loader = providers.Factory(ArchitectureMapLoader, config=config)
