from dependency_injector import containers, providers

from .config import ShapeConfig
from .resolvers import ShapeResolversContainer


class ShapeContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=ShapeConfig)
    resolvers = providers.Container(ShapeResolversContainer)
    catalog = resolvers.container.catalog
