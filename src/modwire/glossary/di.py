from pathlib import Path

from dependency_injector import containers, providers

from .app import GlossaryApplication
from .services import GlossaryRenderer, GlossaryRepository


class GlossaryContainer(containers.DeclarativeContainer):
    cwd = providers.Dependency(instance_of=Path)

    repository = providers.Singleton(
        GlossaryRepository,
        root=cwd,
    )

    renderer = providers.Singleton(GlossaryRenderer)

    app = providers.Factory(
        GlossaryApplication,
        repository=repository,
        renderer=renderer,
    )
