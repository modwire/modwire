from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ScaffoldingApplication
from .config import ScaffoldingConfigResolver
from .services import ScaffoldRepository, CodePackageWriter


class ScaffoldingContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    scaffolding_config_resolver = providers.Factory(
        ScaffoldingConfigResolver,
        config_resolver=config_resolver,
    )

    config = providers.Singleton(
        lambda resolver: resolver.resolve(),
        resolver=scaffolding_config_resolver,
    )

    repository = providers.Singleton(
        ScaffoldRepository,
        config=config
    )

    writer = providers.Singleton(
        CodePackageWriter
    )

    app = providers.Factory(
        ScaffoldingApplication,
        repository=repository,
        writer=writer,
    )
