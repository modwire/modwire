from dependency_injector import containers, providers

from ..base import FlowAnalyzerInterface

from .catalog import FlowAnalyzerCatalog
from .backward import BackwardFlowAnalyzer
from .no_cycles import NoCyclesFlowAnalyzer
from .no_reentry import NoReentryFlowAnalyzer


def _default_flow_analyzers() -> list[FlowAnalyzerInterface]:
    return [
        BackwardFlowAnalyzer(),
        NoCyclesFlowAnalyzer(),
        NoReentryFlowAnalyzer(),
    ]


class FlowAnalyzersContainer(containers.DeclarativeContainer):
    catalog = providers.Singleton(
        FlowAnalyzerCatalog,
        analyzers=providers.Callable(_default_flow_analyzers),
    )
