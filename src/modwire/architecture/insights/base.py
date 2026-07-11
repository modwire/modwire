import abc

from modwire.shared import report

from ..map.base import ArchitectureMap


class InsightReporterInterface(abc.ABC):
    name: str
    report_type: type[report.ReportItem]

    @abc.abstractmethod
    def collect(self, architecture_map: ArchitectureMap) -> report.ReportItem:
        raise NotImplementedError
