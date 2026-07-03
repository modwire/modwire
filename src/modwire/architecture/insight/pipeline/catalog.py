from ..base import InsightReporter
from ..reports import ClustersReporter, HotspotsReporter, CoherenceReporter, CallablesReporter, ExportsReporter


class InsightReporterCatalog:
    def __init__(self):
        self._reporters = {
            reporter.name: reporter
            for reporter in (
                ClustersReporter(),
                HotspotsReporter(),
                CoherenceReporter(),
                CallablesReporter(),
                ExportsReporter(),
            )
        }

    def reporter(self, name: str) -> InsightReporter:
        try:
            return self._reporters[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._reporters))
            raise ValueError(
                f"Unknown insight reporter {name!r}. Known reporters: {known}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._reporters)
