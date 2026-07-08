from dependency_injector import containers, providers

from .config import ShapeConfig
from .reports import ShapeReportsContainer
from .resolvers import ShapeResolversContainer


class ShapeContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=ShapeConfig)
    resolvers = providers.Container(ShapeResolversContainer)
    catalog = resolvers.container.catalog

    reports = providers.Container(
        ShapeReportsContainer,
        config=config,
        catalog=catalog,
    )
