from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import LayersApplication
from .config import LayersConfig


class LayersContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)
    
    config = providers.Singleton(
        lambda resolver: resolver.resolve("layers", LayersConfig),
        resolver=config_resolver,
    )

    app = providers.Factory(LayersApplication)
