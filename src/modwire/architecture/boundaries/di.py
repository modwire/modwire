from dependency_injector import containers, providers

from .config import BoundariesConfig
from .analyzers import FlowAnalyzersContainer
from .analyzer import FlowRealmSelector, BoundariesFlowAnalyzer
from .reports import BoundariesReportsContainer


class BoundariesContainer(containers.DeclarativeContainer):
    config = providers.Dependency(instance_of=BoundariesConfig)
    analyzers = providers.Container(FlowAnalyzersContainer)
    flow_realm_selector = providers.Singleton(FlowRealmSelector)

    flow_analyzer = providers.Factory(
        BoundariesFlowAnalyzer,
        config=config,
        catalog=analyzers.container.catalog,
        realm_selector=flow_realm_selector,
    )

    reports = providers.Container(
        BoundariesReportsContainer,
        flow_analyzer=flow_analyzer,
    )
