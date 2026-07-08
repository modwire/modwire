from typing import TYPE_CHECKING, ClassVar

from ...base import ReportCategory, ReportItem
from .base import InsightReporter


if TYPE_CHECKING:
    from ...map import ArchitectureMap


class CoherenceReport(ReportItem):
    report_id: ClassVar[str] = "architecture.insights.coherence"
    report_title: ClassVar[str] = "Dependency Coherence"
    report_category: ClassVar[ReportCategory] = ReportCategory.INSIGHT
    report_path: ClassVar[str] = "insights.coherence"
    report_order: ClassVar[int] = 30

    roots: tuple[str, ...] = ()
    leaves: tuple[str, ...] = ()
    isolated: tuple[str, ...] = ()
    external_dependencies: tuple[str, ...] = ()


class CoherenceReporter(InsightReporter):
    name: str = "coherence"
    title: str = "Dependency Coherence"

    def collect(self, architecture_map: "ArchitectureMap") -> CoherenceReport:
        source_ids = set(architecture_map.code_map.source_ids())
        roots: list[str] = []
        leaves: list[str] = []
        isolated: list[str] = []

        for source_id in sorted(source_ids):
            has_incoming = (
                architecture_map.code_map.incoming_dependencies(source_id).count() > 0
            )
            has_outgoing = (
                architecture_map.code_map.outgoing_dependencies(source_id).count() > 0
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

        return CoherenceReport(
            roots=tuple(roots),
            leaves=tuple(leaves),
            isolated=tuple(isolated),
            external_dependencies=tuple(sorted(external_dependencies)),
        )
