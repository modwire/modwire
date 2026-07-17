"""Supported, transport-neutral Architecture analysis result contract."""

from enum import StrEnum
from typing import Literal

from modwire_architecture.shared import ModwireReportModel


class AnalysisStatus(StrEnum):
    """The explicit result state for an Architecture assessment."""

    PASS = "pass"
    VIOLATION = "violation"
    NOT_APPLICABLE = "not-applicable"
    UNSUPPORTED = "unsupported"


class FindingSeverity(StrEnum):
    """Severity assigned by Architecture, independent of transport presentation."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class EvidenceFact(ModwireReportModel):
    """A stable, serializable fact supporting an assessment."""

    name: str
    value: str


class AnalysisEvidence(ModwireReportModel):
    """Traceable source and rule evidence for one assessment."""

    report_id: str
    rule_id: str = ""
    source_ids: tuple[str, ...] = ()
    facts: tuple[EvidenceFact, ...] = ()


class AnalysisOutcome(ModwireReportModel):
    """One explicit pass, violation, not-applicable, or unsupported assessment."""

    id: str
    category: str
    status: AnalysisStatus
    severity: FindingSeverity
    summary: str
    evidence: AnalysisEvidence


class ArchitectureInsight(ModwireReportModel):
    """A deterministic insight payload retained separately from policy outcomes."""

    id: str
    title: str
    payload: dict[str, object]


class ArchitectureAnalysis(ModwireReportModel):
    """Versioned public result of pure Architecture analysis."""

    schema_version: Literal[1] = 1
    outcomes: tuple[AnalysisOutcome, ...] = ()
    insights: tuple[ArchitectureInsight, ...] = ()
