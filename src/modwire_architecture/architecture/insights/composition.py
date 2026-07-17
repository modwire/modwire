from .collector import InsightReportCollector
from .reporters.callables import CallablesReporter
from .reporters.clusters import ClustersReporter
from .reporters.coherence import CoherenceReporter
from .reporters.exports import ExportsReporter
from .reporters.hotspots import HotspotsReporter


def standard_insight_report_collector():
    return InsightReportCollector(
        (
            CallablesReporter(),
            ClustersReporter(),
            CoherenceReporter(),
            ExportsReporter(),
            HotspotsReporter(),
        )
    )
