from dependency_injector import containers, providers

from modwire.shared import ConfigResolver

from .boundaries import BoundariesContainer
from .insights import InsightsContainer
from .map import MapContainer
from .shape import ShapeContainer

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

    boundaries_config = providers.Singleton(
        lambda config: config.boundaries,
        config=config,
    )

    shape_config = providers.Singleton(
        lambda config: config.shape,
        config=config,
    )

    boundaries = providers.Container(
        BoundariesContainer,
        config=boundaries_config,
    )

    shape = providers.Container(
        ShapeContainer,
        config=shape_config,
    )

    insights = providers.Container(InsightsContainer)

    map = providers.Container(
        MapContainer,
        config=config,
    )

    app = providers.Factory(
        ArchitectureApplication,
        config=config,
        map_loader=map.container.loader,
        flow_analyzer=boundaries.container.flow_analyzer,
        shape_catalog=shape.container.catalog,
    )
