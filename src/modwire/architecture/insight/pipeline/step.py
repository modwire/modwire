import abc

from ...boundaries.map import ArchitectureMap

from .catalog import InsightReporterCatalog
from .report import InsightReport


class InsightPipelineStepInterface(abc.ABC):
    @abc.abstractmethod
    def run(self, architecture_map: ArchitectureMap) -> InsightReport:
        raise NotImplementedError


class InsightPipelineStep(InsightPipelineStepInterface):
    def __init__(
        self,
        reporters: tuple[str, ...],
    ):
        self.catalog = InsightReporterCatalog()
        self.reporters = reporters

    def run(self, architecture_map: ArchitectureMap) -> InsightReport:
        return InsightReport.model_validate({})
