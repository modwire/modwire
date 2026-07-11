from modwire.shared import config

from .boundaries.analyzer import BoundariesFlowAnalyzer
from .boundaries.analyzers.backward import BackwardFlowAnalyzer
from .boundaries.analyzers.module_boundaries import ModuleBoundaryAnalyzer
from .boundaries.analyzers.no_cycles import NoCyclesFlowAnalyzer
from .boundaries.analyzers.no_reentry import NoReentryFlowAnalyzer
from .boundaries.collector import FlowReportCollector
from .insights.collector import InsightReportCollector
from .insights.reporters.callables import CallablesReporter
from .insights.reporters.clusters import ClustersReporter
from .insights.reporters.coherence import CoherenceReporter
from .insights.reporters.exports import ExportsReporter
from .insights.reporters.hotspots import HotspotsReporter
from .map import ArchitectureMapLoader, MapReportCollector
from .shape.collector import ShapeReportCollector
from .shape.resolvers.abstract_class_resolver import AbstractClassResolver
from .shape.resolvers.callable_resolver import CallableResolver
from .shape.resolvers.class_resolver import ClassResolver
from .shape.resolvers.file_resolver import FileResolver
from .shape.resolvers.import_resolver import ImportResolver
from .shape.resolvers.property_resolver import PropertyResolver
from .shape.resolvers.signature_resolver import SignatureResolver
from .shape.resolvers.symbol_resolver import SymbolResolver


def standard_architecture_components(
    config_: config.ArchitectureConfig,
):
    flow_analyzer = BoundariesFlowAnalyzer(
        config_,
        (
            BackwardFlowAnalyzer(),
            ModuleBoundaryAnalyzer(config_.boundaries),
            NoCyclesFlowAnalyzer(),
            NoReentryFlowAnalyzer(),
        ),
    )
    symbol_resolver = SymbolResolver(
        (
            AbstractClassResolver(),
            CallableResolver(),
            ClassResolver(),
            PropertyResolver(),
            SignatureResolver(),
        )
    )
    return (
        ArchitectureMapLoader(config_),
        (
            MapReportCollector(),
            FlowReportCollector(flow_analyzer),
            InsightReportCollector(
                (
                    CallablesReporter(),
                    ClustersReporter(),
                    CoherenceReporter(),
                    ExportsReporter(),
                    HotspotsReporter(),
                )
            ),
            ShapeReportCollector(
                config_,
                (FileResolver(), ImportResolver(), symbol_resolver),
            ),
        ),
    )
