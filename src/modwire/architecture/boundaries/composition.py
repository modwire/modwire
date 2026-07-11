from modwire.shared.config import ArchitectureConfig

from .analyzer import BoundariesFlowAnalyzer
from .analyzers.backward import BackwardFlowAnalyzer
from .analyzers.module_boundaries import ModuleBoundaryAnalyzer
from .analyzers.no_cycles import NoCyclesFlowAnalyzer
from .analyzers.no_reentry import NoReentryFlowAnalyzer
from .collector import FlowReportCollector


def standard_flow_report_collector(config: ArchitectureConfig):
    return FlowReportCollector(
        BoundariesFlowAnalyzer(
            config,
            (
                BackwardFlowAnalyzer(),
                ModuleBoundaryAnalyzer(config.boundaries),
                NoCyclesFlowAnalyzer(),
                NoReentryFlowAnalyzer(),
            ),
        )
    )
