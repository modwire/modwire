from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ModulesApplication
from .config import ModulesConfigResolver


class ModulesContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    modules_config_resolver = providers.Factory(
        ModulesConfigResolver,
        config_resolver=config_resolver,
    )

    config = providers.Singleton(
        lambda resolver: resolver.resolve(),
        resolver=modules_config_resolver,
    )

    app = providers.Factory(ModulesApplication)
