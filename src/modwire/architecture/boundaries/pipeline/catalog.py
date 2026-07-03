from ..analyzers import (
    BackwardFlowAnalyzer, 
    NoCyclesFlowAnalyzer, 
    NoReentryFlowAnalyzer,
)


class FlowAnalyzerCatalog:
    def __init__(self):
        self._analyzers = {
            analyzer.name: analyzer
            for analyzer in (
                BackwardFlowAnalyzer(),
                NoCyclesFlowAnalyzer(),
                NoReentryFlowAnalyzer(),
            )
        }

    def analyzer(self, name: str):
        try:
            return self._analyzers[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._analyzers))
            raise ValueError(f"Unknown flow analyzer {name!r}. Known analyzers: {known}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._analyzers)
