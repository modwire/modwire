from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import LayersApplication
from .config import LayersConfigResolver


class LayersContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)
    
    layers_config_resolver = providers.Factory(
        LayersConfigResolver,
        config_resolver=config_resolver,
    )

    config = providers.Singleton(
        lambda resolver: resolver.resolve(),
        resolver=layers_config_resolver,
    )

    app = providers.Factory(LayersApplication)
