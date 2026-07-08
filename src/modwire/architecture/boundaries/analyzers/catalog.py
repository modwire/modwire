from collections.abc import Sequence

from wireup import injectable

from ..base import FlowAnalyzerInterface


@injectable
class FlowAnalyzerCatalog:
    def __init__(
        self,
        analyzers: Sequence[FlowAnalyzerInterface],
    ):
        self._analyzers = {analyzer.name: analyzer for analyzer in analyzers}

    def analyzer(self, name: str) -> FlowAnalyzerInterface:
        try:
            return self._analyzers[name]
        except KeyError as error:
            known = ", ".join(sorted(self._analyzers))
            raise ValueError(
                f"Unknown flow analyzer {name!r}. Known analyzers: {known}"
            ) from error

    def names(self) -> tuple[str, ...]:
        return tuple(self._analyzers)
