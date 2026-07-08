from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ScaffoldingApplication
from .config import ScaffoldingConfig
from .services import ScaffoldRepository, CodePackageWriter


class ScaffoldingContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    config = providers.Singleton(
        lambda resolver: resolver.resolve("scaffolding", ScaffoldingConfig, default=ScaffoldingConfig(scaffolds_root=resolver.root)),
        resolver=config_resolver,
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
