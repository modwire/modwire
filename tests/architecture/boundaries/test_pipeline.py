from modwire.architecture.boundaries.config import (
    BoundariesConfig,
    FlowRealm,
    FlowRules,
    TagRule,
)
from modwire.architecture.boundaries.map import ArchitectureMapLoader
from modwire.architecture.boundaries.pipeline import FlowPipelineStep
from modwire.architecture.config import ArchitectureConfig
from modwire_extraction.code import CodeMap, QueryableCodeMap
from modwire_extraction.dependency.graph import DependencyGraph
from modwire_extraction.extractors.languages.base import SourceExtraction
from modwire_extraction.extractors.source import SourceFile


def test_flow_pipeline_runs_backward_analyzer_for_realms():
    graph = DependencyGraph()
    graph.add_edge("features/billing/ui/view", "features/billing/domain/model")
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
                analyzers=("backward-flow",),
            ),
        ),
    )
    architecture_map = ArchitectureMapLoader(config).load(
        code_map=queryable_code_map(
            (
                "features/billing/ui/view",
                "features/billing/domain/model",
            ),
            graph,
        ),
    )

    report = FlowPipelineStep().run(architecture_map)

    assert report.analyzers == ("backward-flow",)
    assert len(report.violations) == 1
    violation = report.violations[0]
    assert violation.violation_type == "backward-flow"
    assert violation.path == (
        "features/billing/ui/view",
        "features/billing/domain/model",
    )
    assert violation.rule_name == "analyzer:feature:backward-flow"


def test_flow_pipeline_runs_cycle_analyzer():
    graph = DependencyGraph()
    graph.add_edge("features/billing/domain/model", "features/orders/domain/model")
    graph.add_edge("features/orders/domain/model", "features/billing/domain/model")
    config = ArchitectureConfig(
        language="python",
        boundaries=BoundariesConfig(
            tags=(
                TagRule(name="module", match="features/*"),
            ),
            flow=FlowRules(
                module_tag="module",
                analyzers=("no-cycles",),
            ),
        ),
    )
    architecture_map = ArchitectureMapLoader(config).load(
        code_map=queryable_code_map(
            (
                "features/billing/domain/model",
                "features/orders/domain/model",
            ),
            graph,
        ),
    )

    report = FlowPipelineStep().run(architecture_map)

    assert report.analyzers == ("no-cycles",)
    assert len(report.violations) == 1
    assert report.violations[0].violation_type == "no-cycles"
    assert report.violations[0].path == ("billing", "orders", "billing")


def queryable_code_map(
    source_ids: tuple[str, ...],
    graph: DependencyGraph,
) -> QueryableCodeMap:
    return QueryableCodeMap(
        CodeMap(
            language="python",
            extraction=SourceExtraction(
                files={
                    source_id: source_file()
                    for source_id in source_ids
                },
                files_found=len(source_ids),
                files_excluded=0,
            ),
            dependency_graph=graph,
        )
    )


def source_file() -> SourceFile:
    return SourceFile(
        imports=[],
        classes=[],
        functions=[],
        line_count=1,
        code_line_count=1,
        public_symbol_count=0,
    )
