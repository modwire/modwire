from dependency_injector import containers, providers

from ..flow import BoundariesFlowAnalyzer
from .flow import FlowReportCollector
from .map import ArchitectureMapReportCollector


class BoundariesReportsContainer(containers.DeclarativeContainer):
    flow_analyzer = providers.Dependency(instance_of=BoundariesFlowAnalyzer)

    map = providers.Factory(ArchitectureMapReportCollector)

    flow = providers.Factory(
        FlowReportCollector,
        flow_analyzer=flow_analyzer,
    )
