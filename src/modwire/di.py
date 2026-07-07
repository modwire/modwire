from pathlib import Path
from typing import Any

from dependency_injector import containers, providers

from .architecture.di import ArchitectureContainer
from .layers.di import LayersContainer
from .modules.di import ModulesContainer
from .projects.di import ProjectsContainer
from .scaffolding.di import ScaffoldingContainer

from .shared import ConfigResolver


class ModwireContainer(containers.DeclarativeContainer):
    cwd = providers.Dependency(instance_of=Path)
    config_resolver = providers.Singleton(ConfigResolver, root=cwd)

    architecture = providers.Container(ArchitectureContainer, config_resolver=config_resolver)
    layers = providers.Container(LayersContainer, config_resolver=config_resolver)
    modules = providers.Container(ModulesContainer, config_resolver=config_resolver)
    projects = providers.Container(ProjectsContainer, config_resolver=config_resolver)
    scaffolding = providers.Container(ScaffoldingContainer, config_resolver=config_resolver)


def load_app(container: ModwireContainer, name: str) -> Any:
    apps = {
        "architecture": container.architecture.app,
        "layers": container.layers.app,
        "modules": container.modules.app,
        "projects": container.projects.app,
        "scaffolding": container.scaffolding.app,
    }

    try:
        return apps[name]()
    except KeyError as error:
        raise ValueError(f"Unknown app: {name}") from error
