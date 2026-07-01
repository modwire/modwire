import pytest

from modwire.architecture.boundaries.map import ArchitectureMapLoader
from modwire.architecture.config import ArchitectureConfig
from modwire.architecture.insight.pipeline import (
    DEFAULT_REPORTERS,
    InsightPipelineStep,
    InsightReporterCatalog,
)
from modwire_extraction.code import CodeMap, QueryableCodeMap
from modwire_extraction.dependency.graph import DependencyGraph
from modwire_extraction.extractors.languages.base import SourceExtraction
from modwire_extraction.extractors.source import (
    SourceCall,
    SourceCallable,
    SourceExport,
    SourceFile,
    SourceImport,
    SourceImportedSymbol,
)


def test_insight_pipeline_runs_concrete_reporters():
    graph = DependencyGraph()
    graph.add_edge("features/billing/api/view", "features/billing/domain/model")
    graph.add_edge("features/billing/domain/model", "shared/logger")
    graph.add_edge("features/billing/api/view", "requests")
    architecture_map = ArchitectureMapLoader(ArchitectureConfig(language="python")).load(
        code_map=queryable_code_map(graph)
    )

    report = InsightPipelineStep().run(architecture_map)

    assert report.reporters == DEFAULT_REPORTERS
    assert report.hotspots[0].source_id == "features/billing/api/view"
    assert report.hotspots[0].pressure_score == 2
    assert report.coherence.roots == ("features/billing/api/view",)
    assert report.coherence.leaves == ("shared/logger",)
    assert report.coherence.external_dependencies == ("requests",)
    assert report.clusters[0].name == "features/billing"
    assert report.clusters[0].outgoing_count == 1

    api_entry = next(
        entry
        for entry in report.callables
        if entry.source_callable == "features/billing/api/view::handler"
    )
    assert api_entry.calls == ("features/billing/domain/model::build",)

    domain_entry = next(
        entry
        for entry in report.callables
        if entry.source_callable == "features/billing/domain/model::build"
    )
    assert domain_entry.callers == ("features/billing/api/view::handler",)

    assert tuple(export.name for export in report.unused_exports) == ("unused",)
    assert report.unused_exports[0].reason == "not imported"


def test_insight_reporter_catalog_rejects_unknown_reporter():
    with pytest.raises(ValueError, match="Unknown insight reporter"):
        InsightReporterCatalog().reporter("missing")


def queryable_code_map(graph: DependencyGraph) -> QueryableCodeMap:
    return QueryableCodeMap(
        CodeMap(
            language="python",
            extraction=SourceExtraction(
                files={
                    "features/billing/api/view": source_file(
                        imports=[
                            SourceImport(
                                path="features.billing.domain.model",
                                is_relative=False,
                                normalized_path="features/billing/domain/model",
                                imported_name="",
                                is_aliased=False,
                                crossing_type="symbol",
                                file_barrier_crossed=False,
                                statement_id=1,
                                join_key="features.billing.domain.model",
                                uses_joined_import=True,
                                imported_symbols=[
                                    SourceImportedSymbol(
                                        name="build",
                                        alias="",
                                        is_aliased=False,
                                        is_default=False,
                                        is_namespace=False,
                                        is_star=False,
                                    )
                                ],
                            )
                        ],
                        callables=[
                            source_callable(
                                "features/billing/api/view::handler",
                                "features/billing/api/view",
                                "handler",
                            )
                        ],
                        calls=[
                            SourceCall(
                                source_callable_id="features/billing/api/view::handler",
                                target_callable_id=(
                                    "features/billing/domain/model::build"
                                ),
                                source_id="features/billing/api/view",
                                line=3,
                                expression="build()",
                                resolution="resolved",
                                target_name="build",
                            )
                        ],
                    ),
                    "features/billing/domain/model": source_file(
                        exports=[
                            SourceExport(
                                name="build",
                                local_name="build",
                                kind="function",
                                crossing_type="symbol",
                                path="",
                                is_relative=False,
                                normalized_path="",
                                is_reexport=False,
                                is_default=False,
                                is_aliased=False,
                                statement_id=1,
                            )
                        ],
                        callables=[
                            source_callable(
                                "features/billing/domain/model::build",
                                "features/billing/domain/model",
                                "build",
                            )
                        ],
                    ),
                    "shared/logger": source_file(
                        exports=[
                            SourceExport(
                                name="unused",
                                local_name="unused",
                                kind="function",
                                crossing_type="symbol",
                                path="",
                                is_relative=False,
                                normalized_path="",
                                is_reexport=False,
                                is_default=False,
                                is_aliased=False,
                                statement_id=1,
                            )
                        ],
                    ),
                },
                files_found=3,
                files_excluded=0,
            ),
            dependency_graph=graph,
        )
    )


def source_file(
    *,
    imports: list[SourceImport] | None = None,
    exports: list[SourceExport] | None = None,
    callables: list[SourceCallable] | None = None,
    calls: list[SourceCall] | None = None,
) -> SourceFile:
    return SourceFile(
        imports=imports or [],
        exports=exports or [],
        classes=[],
        functions=[],
        callables=callables or [],
        calls=calls or [],
        line_count=1,
        code_line_count=1,
        public_symbol_count=0,
    )


def source_callable(
    callable_id: str,
    source_id: str,
    name: str,
) -> SourceCallable:
    return SourceCallable(
        id=callable_id,
        source_id=source_id,
        name=name,
        qualified_name=name,
        kind="function",
        visibility="public",
        visibility_intent="public",
        line_start=1,
        line_end=1,
        line_count=1,
    )
