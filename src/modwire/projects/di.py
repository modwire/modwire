from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .app import ProjectsApplication
from .config import ProjectsConfigResolver


class ProjectsContainer(containers.DeclarativeContainer):
    config_resolver = providers.Dependency(instance_of=ConfigResolver)

    projects_config_resolver = providers.Factory(
        ProjectsConfigResolver,
        config_resolver=config_resolver,
    )

    config = providers.Singleton(
        lambda resolver: resolver.resolve(),
        resolver=projects_config_resolver,
    )
    
    app = providers.Factory(ProjectsApplication, config=config)
