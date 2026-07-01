from modwire.architecture.boundaries.config import BoundariesConfig, FlowRules, TagRule
from modwire.architecture.boundaries.map import load_architecture_map
from modwire.architecture.config import ArchitectureConfig
from modwire_extraction.code import CodeMap, QueryableCodeMap
from modwire_extraction.dependency.graph import DependencyGraph
from modwire_extraction.extractors.languages.base import SourceExtraction
from modwire_extraction.extractors.source import SourceFile


def test_load_architecture_map_indexes_tags_modules_and_layers():
    code_map = QueryableCodeMap(
        CodeMap(
            language="python",
            extraction=SourceExtraction(
                files={
                    "features/billing/ui/view": source_file(),
                    "features/billing/domain/model": source_file(),
                    "shared/logger": source_file(),
                },
                files_found=3,
                files_excluded=0,
            ),
            dependency_graph=DependencyGraph(),
        )
    )
    config = ArchitectureConfig(
        language="python",
        boundaries=BoundariesConfig(
            tags=(
                TagRule(name="module", match="features/*"),
                TagRule(name="ui", match="features/*/ui"),
                TagRule(name="domain", match="features/*/domain"),
            ),
            flow=FlowRules(
                module_tag="module",
                layers=("ui", "domain"),
            ),
        ),
    )

    architecture_map = load_architecture_map(config, code_map)

    assert architecture_map.code_map is code_map
    assert architecture_map.modules == {
        "billing": (
            "features/billing/domain/model",
            "features/billing/ui/view",
        ),
    }
    assert architecture_map.layers == {
        "domain": ("features/billing/domain/model",),
        "ui": ("features/billing/ui/view",),
    }
    assert architecture_map.unknown_files == ("shared/logger",)
    assert tuple(architecture_map.tag_map.matches_by_node) == (
        "features/billing/ui/view",
        "features/billing/domain/model",
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
