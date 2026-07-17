"""Normalize legacy collector output into the supported analysis contract."""

from collections.abc import Iterable
from typing import cast

from modwire_architecture.shared import config, report

from .boundaries.collector import FlowReport
from .contract import (
    AnalysisEvidence,
    AnalysisOutcome,
    AnalysisStatus,
    ArchitectureAnalysis,
    ArchitectureInsight,
    EvidenceFact,
    FindingSeverity,
)
from .insights.reporters.base import InsightReport
from .shape.collector import ShapeReport


def normalize_analysis(
    config_: config.ArchitectureConfig,
    reports: Iterable[report.ReportNode],
) -> ArchitectureAnalysis:
    """Return the stable public analysis envelope for collector output."""
    materialized = tuple(reports)
    flow = next(item for item in materialized if isinstance(item, FlowReport))
    shape = next(item for item in materialized if isinstance(item, ShapeReport))
    insights = next(item for item in materialized if isinstance(item, InsightReport))
    outcomes = (
        *_flow_outcomes(config_, flow),
        *_shape_outcomes(shape),
    )
    return ArchitectureAnalysis(
        outcomes=tuple(sorted(outcomes, key=lambda outcome: outcome.id)),
        insights=_insights(insights),
    )


def _flow_outcomes(
    config_: config.ArchitectureConfig,
    flow: FlowReport,
) -> tuple[AnalysisOutcome, ...]:
    if not _has_boundary_policy(config_):
        return (
            AnalysisOutcome(
                id="boundaries:not-applicable",
                category="boundaries",
                status=AnalysisStatus.NOT_APPLICABLE,
                severity=FindingSeverity.INFO,
                summary="No boundary policy is configured.",
                evidence=AnalysisEvidence(report_id=flow.metadata.id),
            ),
        )
    if not flow.violations:
        return (
            AnalysisOutcome(
                id="boundaries:pass",
                category="boundaries",
                status=AnalysisStatus.PASS,
                severity=FindingSeverity.INFO,
                summary="Configured boundary policies reported no violations.",
                evidence=AnalysisEvidence(report_id=flow.metadata.id),
            ),
        )
    return tuple(
        AnalysisOutcome(
            id=(
                f"boundaries:{violation.rule_name}:{violation.violation_index}:"
                f"{'|'.join(violation.path)}"
            ),
            category="boundaries",
            status=AnalysisStatus.VIOLATION,
            severity=FindingSeverity.ERROR,
            summary=violation.message,
            evidence=AnalysisEvidence(
                report_id=flow.metadata.id,
                rule_id=violation.rule_name,
                source_ids=violation.path,
                facts=tuple(
                    fact
                    for fact in (
                        EvidenceFact(name="violation_type", value=violation.violation_type),
                        _fact("source_module", violation.source_module),
                        _fact("target_module", violation.target_module),
                    )
                    if fact is not None
                ),
            ),
        )
        for violation in sorted(flow.violations, key=lambda item: item.violation_key())
    )


def _shape_outcomes(shape: ShapeReport) -> tuple[AnalysisOutcome, ...]:
    if not shape.violations:
        return (
            AnalysisOutcome(
                id="shape:pass",
                category="shape",
                status=AnalysisStatus.PASS,
                severity=FindingSeverity.INFO,
                summary="Configured shape policies reported no violations.",
                evidence=AnalysisEvidence(report_id=shape.metadata.id),
            ),
        )
    violations = tuple(
        sorted(
            shape.violations,
            key=lambda item: (
                item.rule_name,
                item.source_id,
                item.symbol_kind,
                item.symbol_name,
                str(item.actual),
                str(item.limit),
            ),
        )
    )
    return tuple(
        AnalysisOutcome(
            id=f"shape:{violation.rule_name}:{index}:{violation.source_id}",
            category="shape",
            status=AnalysisStatus.VIOLATION,
            severity=FindingSeverity.ERROR,
            summary=(
                f"{violation.rule_name} violated by {violation.source_id}: "
                f"actual {violation.actual}, limit {violation.limit}."
            ),
            evidence=AnalysisEvidence(
                report_id=shape.metadata.id,
                rule_id=violation.rule_name,
                source_ids=(violation.source_id,),
                facts=tuple(
                    fact
                    for fact in (
                        EvidenceFact(name="actual", value=str(violation.actual)),
                        EvidenceFact(name="limit", value=str(violation.limit)),
                        _fact("symbol_kind", violation.symbol_kind),
                        _fact("symbol_name", violation.symbol_name),
                    )
                    if fact is not None
                ),
            ),
        )
        for index, violation in enumerate(violations, start=1)
    )


def _insights(insights: InsightReport) -> tuple[ArchitectureInsight, ...]:
    items = tuple(
        cast(report.ReportItem, getattr(insights, field_name))
        for field_name in ("clusters", "hotspots", "coherence", "callables", "exports")
    )
    return tuple(
        ArchitectureInsight(
            id=item.metadata.id,
            title=item.metadata.title,
            payload=item.model_dump(mode="json"),
        )
        for item in sorted(items, key=lambda item: (item.metadata.order, item.metadata.id))
    )


def _has_boundary_policy(config_: config.ArchitectureConfig) -> bool:
    boundaries = config_.boundaries
    flow = boundaries.flow
    return bool(
        boundaries.tags
        or boundaries.rules
        or flow.layers
        or flow.module_tag
        or flow.realms
        or flow.analyzers
    )


def _fact(name: str, value: str) -> EvidenceFact | None:
    return EvidenceFact(name=name, value=value) if value else None
