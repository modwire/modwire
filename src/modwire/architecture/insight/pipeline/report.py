from modwire.shared import ModwireBaseModel

from ..reports import ClustersReport, HotspotsReport, CoherenceReport, CallablesReport, ExportsReport


class InsightReport(ModwireBaseModel):
    clusters: ClustersReport
    hotspots: HotspotsReport
    coherence: CoherenceReport
    callables: CallablesReport
    exports: ExportsReport
