from wireup import injectable

from modwire.shared import report

from ...map.base import ArchitectureMap
from ..base import InsightReporterInterface


class CoherenceReport(report.ReportItem):
    report_id: str = "architecture.insights.coherence"
    report_title: str = "Dependency Coherence"
    report_path: str = "insights.coherence"
    report_order: int = 30

    roots: tuple[str, ...] = ()
    leaves: tuple[str, ...] = ()
    isolated: tuple[str, ...] = ()
    external_dependencies: tuple[str, ...] = ()


@injectable(qualifier="coherence", as_type=InsightReporterInterface)
class CoherenceReporter(InsightReporterInterface):
    name: str = "coherence"
    report_type: type[CoherenceReport] = CoherenceReport

    def collect(self, architecture_map: ArchitectureMap) -> CoherenceReport:
        source_ids = set(architecture_map.code_map.source_ids())
        roots: list[str] = []
        leaves: list[str] = []
        isolated: list[str] = []

        for source_id in sorted(source_ids):
            has_incoming = (
                architecture_map.code_map.incoming_dependencies(
                    source_id).count() > 0
            )
            has_outgoing = (
                architecture_map.code_map.outgoing_dependencies(
                    source_id).count() > 0
            )
            if not has_incoming:
                roots.append(source_id)
            if not has_outgoing:
                leaves.append(source_id)
            if not has_incoming and not has_outgoing:
                isolated.append(source_id)

        external_dependencies = {
            edge_result.edge.from_id
            for edge_result in architecture_map.code_map.external_dependency_edges().all()
            if edge_result.edge.from_id not in source_ids
        }
        external_dependencies.update(
            edge_result.edge.to_id
            for edge_result in architecture_map.code_map.external_dependency_edges().all()
            if edge_result.edge.to_id not in source_ids
        )

        return self.report_type(
            roots=tuple(roots),
            leaves=tuple(leaves),
            isolated=tuple(isolated),
            external_dependencies=tuple(sorted(external_dependencies)),
        )
