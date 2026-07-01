from modwire.architecture import (
    ArchitectureConfig,
    ArchitectureReportRunner,
)
from modwire.architecture.boundaries.config import (
    BoundariesConfig,
    FlowRealm,
    FlowRules,
    TagRule,
)
from modwire.architecture.shape.config import ShapeConfig
from modwire_extraction.code import CodeMap, QueryableCodeMap
from modwire_extraction.dependency.graph import DependencyGraph
from modwire_extraction.extractors.languages.base import SourceExtraction
from modwire_extraction.extractors.source import SourceFile, SourceFunction


def test_architecture_report_runner_returns_full_report():
    graph = DependencyGraph()
    graph.add_edge("features/billing/ui/view", "features/billing/domain/model")
    code_map = queryable_code_map(
        {
            "features/billing/ui/view": source_file(functions=(source_function(),)),
            "features/billing/domain/model": source_file(),
        },
        graph,
    )
    config = ArchitectureConfig(
        language="python",
        boundaries=BoundariesConfig(
            tags=(
                TagRule(name="ui", match="features/*/ui"),
                TagRule(name="domain", match="features/*/domain"),
            ),
            flow=FlowRules(
                realms=(
                    FlowRealm(
                        name="feature",
                        layers=("domain", "ui"),
                    ),
                ),
            ),
        ),
        shape=ShapeConfig(max_functions_per_file=0),
    )

    report = ArchitectureReportRunner(config).run(code_map)

    assert report.map.layers[0].name == "domain"
    assert report.map.layers[1].name == "ui"
    assert len(report.violations.flow.violations) == 1
    assert report.violations.flow.violations[0].violation_type == "backward-flow"
    assert len(report.violations.shape.violations) == 1
    assert report.violations.shape.violations[0].rule_name == "max_functions_per_file"
    assert len(report.insights.clusters) == 1
    assert len(report.insights.hotspots) == 2


def test_architecture_report_runner_handles_empty_config():
    code_map = queryable_code_map({"app/main": source_file()}, DependencyGraph())
    config = ArchitectureConfig(language="python")

    report = ArchitectureReportRunner(config).run(code_map)

    assert report.map.unknown_files == ("app/main",)
    assert report.violations.flow.violations == ()
    assert report.violations.shape.violations == ()
    assert len(report.insights.hotspots) == 1


def queryable_code_map(
    source_files: dict[str, SourceFile],
    graph: DependencyGraph,
) -> QueryableCodeMap:
    return QueryableCodeMap(
        CodeMap(
            language="python",
            extraction=SourceExtraction(
                files=source_files,
                files_found=len(source_files),
                files_excluded=0,
            ),
            dependency_graph=graph,
        )
    )


def source_file(functions: tuple[SourceFunction, ...] = ()) -> SourceFile:
    return SourceFile(
        imports=[],
        classes=[],
        functions=list(functions),
        line_count=1,
        code_line_count=1,
        public_symbol_count=len(functions),
    )


def source_function() -> SourceFunction:
    return SourceFunction(
        name="view",
        visibility="public",
        visibility_intent="public",
        line_count=1,
        declared_args=0,
        optional_args=0,
    )
