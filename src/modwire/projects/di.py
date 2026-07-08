from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ProjectsApplication
from .config import ProjectsConfig


class ProjectsContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    config = providers.Singleton(
        lambda resolver: resolver.resolve("projects", ProjectsConfig),
        resolver=config_resolver,
    )
    
    app = providers.Factory(ProjectsApplication, config=config)
