from dependency_injector import containers, providers

from modwire.shared import ConfigResolver
from modwire.shared.code import package

from .app import ScaffoldingApplication
from .config import ScaffoldingConfig
from .services import ScaffoldRepository


class ScaffoldingContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)
    code_package_writer = providers.Dependency(instance_of=package.CodePackageWriter)

    config = providers.Singleton(
        lambda resolver: resolver.resolve(
            "scaffolding", 
            ScaffoldingConfig, 
            default=ScaffoldingConfig(scaffolds_root=resolver.root)
        ),
        resolver=config_resolver,
    )

    repository = providers.Singleton(
        ScaffoldRepository,
        config=config
    )

    app = providers.Factory(
        ScaffoldingApplication,
        repository=repository,
        writer=code_package_writer,
    )
