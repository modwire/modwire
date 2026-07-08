from dependency_injector import containers, providers

from ..config import ShapeConfig
from .violations import ShapeReportCollector


class ShapeReportsContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=ShapeConfig)
    catalog = providers.Dependency()

    violations = providers.Factory(
        ShapeReportCollector,
        config=config,
        catalog=catalog,
    )
