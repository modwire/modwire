from modwire_architecture import (
    AnalysisEvidence,
    AnalysisOutcome,
    AnalysisStatus,
    ArchitectureConfig,
    FindingSeverity,
    Modwire,
)
from modwire_architecture.architecture import ArchitectureApplication
from modwire_extraction.code import CodeMap, QueryableCodeMap


def test_standard_architecture_application_exposes_stable_report_catalog() -> None:
    catalog = ArchitectureApplication.standard(ArchitectureConfig()).reports()

    assert tuple(report.id for report in catalog.reports) == (
        "architecture.map",
        "architecture.violations.flow",
        "architecture.violations.shape",
        "architecture.insights",
    )
    assert tuple(child.id for child in catalog.reports[-1].children) == (
        "architecture.insights.clusters",
        "architecture.insights.hotspots",
        "architecture.insights.coherence",
        "architecture.insights.callables",
        "architecture.insights.exports",
    )


def test_public_analysis_contract_is_deterministic_and_explicit() -> None:
    application = Modwire().architecture(ArchitectureConfig())

    first = application.analyze(queryable_map("src/example.py"))
    second = application.analyze(queryable_map("src/example.py"))

    assert first == second
    assert first.schema_version == 1
    assert tuple(outcome.status for outcome in first.outcomes) == (
        AnalysisStatus.NOT_APPLICABLE,
        AnalysisStatus.PASS,
    )
    assert tuple(insight.id for insight in first.insights) == (
        "architecture.insights.clusters",
        "architecture.insights.hotspots",
        "architecture.insights.coherence",
        "architecture.insights.callables",
        "architecture.insights.exports",
    )


def test_public_analysis_contract_preserves_violation_evidence() -> None:
    config = ArchitectureConfig(
        boundaries={
            "tags": ({"name": "backend", "match": "backend/*"},),
            "flow": {
                "realms": ({"name": "backend", "module_tag": "backend"},),
                "analyzers": ("no-cycles",),
            },
        }
    )
    analysis = Modwire().architecture(config).analyze(
        queryable_map(
            "backend/a.py",
            "backend/b.py",
            edges=(
                ("backend/a.py", "backend/b.py", "resolved", "backend.b"),
                ("backend/b.py", "backend/a.py", "resolved", "backend.a"),
            ),
        )
    )

    violation = next(
        outcome
        for outcome in analysis.outcomes
        if outcome.category == "boundaries"
    )

    assert violation.status is AnalysisStatus.VIOLATION
    assert violation.evidence.report_id == "architecture.violations.flow"
    assert violation.evidence.rule_id == "analyzer:backend:no-cycles"
    assert violation.evidence.source_ids == ("a.py", "b.py", "a.py")
    assert violation.evidence.facts[0].name == "violation_type"


def test_public_analysis_outcomes_support_every_explicit_state() -> None:
    outcomes = tuple(
        AnalysisOutcome(
            id=f"test:{status}",
            category="test",
            status=status,
            severity=FindingSeverity.INFO,
            summary="Explicit test state.",
            evidence=AnalysisEvidence(report_id="test"),
        )
        for status in AnalysisStatus
    )

    assert tuple(outcome.status for outcome in outcomes) == tuple(AnalysisStatus)


def queryable_map(
    *paths: str,
    edges: tuple[tuple[str, str | None, str, str], ...] = (),
) -> QueryableCodeMap:
    files = {
        path: {
            "file_id": path,
            "module_id": path.rsplit(".", 1)[0],
            "imports": [],
            "exports": [],
            "classes": [],
            "interfaces": [],
            "types": [],
            "abstract_classes": [],
            "functions": [],
            "values": [],
            "callables": [],
            "calls": [],
            "line_count": 1,
            "code_line_count": 1,
            "public_symbol_count": 0,
        }
        for path in paths
    }
    code_map = CodeMap.from_dict(
        {
            "language": "test",
            "extraction": {
                "files": files,
                "modules": {
                    source["module_id"]: file_id
                    for file_id, source in files.items()
                },
                "files_found": len(files),
                "files_excluded": 0,
            },
            "dependency_graph": {
                "nodes": {path: {"id": path, "kind": "file"} for path in paths},
                "edges": [
                    {
                        "from_id": source,
                        "to_id": target,
                        "specifier": specifier,
                        "resolution": resolution,
                        "kind": "import",
                    }
                    for source, target, resolution, specifier in edges
                ],
            },
        }
    )
    return QueryableCodeMap(code_map=code_map)
