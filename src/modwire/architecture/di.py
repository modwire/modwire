from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ArchitectureApplication
from .config import ArchitectureConfigResolver


class ArchitectureContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    architecture_config_resolver = providers.Factory(
        ArchitectureConfigResolver,
        config_resolver=config_resolver,
    )

    config = providers.Singleton(
        lambda resolver: resolver.resolve(),
        resolver=architecture_config_resolver,
    )

    app = providers.Factory(
        ArchitectureApplication,
        config=config,
    )
