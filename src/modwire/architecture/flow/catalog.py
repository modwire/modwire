from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .backward import BackwardFlowAnalyzer
from .base import FlowAnalysisContext, FlowAnalyzer, FlowViolation
from .no_cycles import NoCyclesFlowAnalyzer
from .no_reentry import NoReentryFlowAnalyzer


class FlowAnalyzerCatalog(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    analyzers: tuple[FlowAnalyzer, ...] = (
        BackwardFlowAnalyzer(),
        NoReentryFlowAnalyzer(),
        NoCyclesFlowAnalyzer(),
    )

    def names(self) -> tuple[str, ...]:
        return tuple(analyzer.name for analyzer in self.analyzers)

    def analyzer(self, name: str) -> FlowAnalyzer:
        for analyzer in self.analyzers:
            if analyzer.name == name:
                return analyzer
        raise KeyError(name)

    def analyze(
        self,
        name: str,
        context: FlowAnalysisContext,
    ) -> tuple[FlowViolation, ...]:
        return self.analyzer(name).analyze(context)
