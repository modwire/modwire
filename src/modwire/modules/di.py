from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ModulesApplication
from .config import ModulesConfig


class ModulesContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    config = providers.Singleton(
        lambda resolver: resolver.resolve("modules", ModulesConfig),
        resolver=config_resolver,
    )

    app = providers.Factory(ModulesApplication)
