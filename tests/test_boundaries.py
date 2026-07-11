from __future__ import annotations

from modwire_extraction.code.code_map import CodeMap
from modwire_extraction.code.query import QueryableCodeMap
from modwire_extraction.dependency.graph import DependencyGraph
from modwire_extraction.extractors.languages.base import SourceExtraction
from modwire_extraction.extractors.source import SourceFile
from modwire_extraction.identity import FileId, ImportSpecifier, ModuleId

from modwire.architecture.boundaries.analyzer import BoundariesFlowAnalyzer
from modwire.architecture.boundaries.analyzers.backward import BackwardFlowAnalyzer
from modwire.architecture.boundaries.analyzers.module_boundaries import (
    ModuleBoundaryAnalyzer,
)
from modwire.architecture.boundaries.base import FlowAnalyzerInterface, FlowViolation
from modwire.architecture.map.loader import ArchitectureMapLoader
from modwire.architecture.app import ArchitectureApplication
from modwire.shared.config.architecture import ArchitectureConfig


class RecordingAnalyzer(FlowAnalyzerInterface):
    def __init__(self) -> None:
        self.realms: list[tuple[str, str, tuple[str, ...]]] = []

    @property
    def name(self) -> str:
        return "recording"

    @property
    def title(self) -> str:
        return "Recording"

    def analyze(self, architecture_map) -> tuple[FlowViolation, ...]:
        realm = architecture_map.realm
        self.realms.append((realm.name, realm.module_tag, realm.layers))
        return ()


def test_flow_analyzers_evaluate_each_configured_realm() -> None:
    config = ArchitectureConfig(
        boundaries={
            "tags": (
                {"name": "backend_module", "match": "backend/*"},
                {"name": "gui_page", "match": "gui/pages/*"},
            ),
            "flow": {
                "realms": (
                    {
                        "name": "backend",
                        "module_tag": "backend_module",
                        "layers": ("application", "domain"),
                    },
                    {"name": "gui", "module_tag": "gui_page"},
                ),
                "analyzers": ("recording",),
            },
        }
    )
    code_map = queryable_map(
        "backend/orders/application.py",
        "gui/pages/home.py",
    )
    architecture_map = ArchitectureMapLoader(config).load(code_map)
    recorder = RecordingAnalyzer()

    assert architecture_map.modules == {
        "home.py": ("gui/pages/home.py",),
        "orders": ("backend/orders/application.py",),
    }
    BoundariesFlowAnalyzer(config, (recorder,)).analyze(architecture_map)
    assert recorder.realms == [
        ("backend", "backend_module", ("application", "domain")),
        ("gui", "gui_page", ()),
    ]
    assert BackwardFlowAnalyzer().analyze(
        architecture_map.with_realm(
            BoundariesFlowAnalyzer(config, (recorder,)).realms(
                config.boundaries.flow
            )[1]
        )
    ) == ()


def test_closed_module_boundaries_cover_all_resolution_states() -> None:
    config = ArchitectureConfig(
        boundaries={
            "tags": (
                {"name": "module", "match": "src/*"},
                {"name": "shared", "match": "src/shared"},
            ),
            "rules": (
                {
                    "source": "module",
                    "disallow": ("module",),
                    "allow": ("shared",),
                    "allow_same_match": True,
                },
                {"source": "shared", "disallow": ("module",)},
            ),
            "flow": {"module_tag": "module"},
        }
    )
    code_map = queryable_map(
        "src/a/one.py",
        "src/a/two.py",
        "src/b/one.py",
        "src/shared/base.py",
        "tools.py",
        edges=(
            ("src/a/one.py", "src/a/two.py", "resolved", "a.two"),
            ("src/a/one.py", "src/shared/base.py", "resolved", "shared.base"),
            ("src/a/one.py", "src/b/one.py", "resolved", "b.one"),
            ("tools.py", "src/a/one.py", "resolved", "a.one"),
            ("src/a/one.py", None, "external", "json"),
            ("src/a/one.py", None, "unresolved", "missing"),
        ),
    )
    architecture_map = ArchitectureMapLoader(config).load(code_map)

    violations = ModuleBoundaryAnalyzer(config.boundaries).analyze(architecture_map)

    assert tuple(violation.rule_name for violation in violations) == (
        "boundary:module",
        "boundary:unclassified",
    )
    forbidden = violations[0]
    assert forbidden.path == ("src/a/one.py", "src/b/one.py")
    assert forbidden.source_module == "module:a"
    assert forbidden.target_module == "module:b"
    assert forbidden.message == (
        "tracked cross-module dependency matches an explicit disallow"
    )
    assert violations[1].path == ("tools.py",)


def test_architecture_application_reports_an_injected_code_map() -> None:
    code_map = queryable_map(
        "src/example/model.py",
        "src/example/service.py",
        edges=(
            (
                "src/example/service.py",
                "src/example/model.py",
                "resolved",
                "example.model",
            ),
            ("src/example/service.py", None, "external", "json"),
            ("src/example/service.py", None, "unresolved", "missing"),
        ),
    )

    application = ArchitectureApplication.standard()
    reports = application.report(code_map)

    assert reports == application.report(code_map)
    assert tuple(node.metadata.id for node in reports) == (
        "architecture.map",
        "architecture.violations.flow",
        "architecture.violations.shape",
        "architecture.insights",
    )


def queryable_map(
    *paths: str,
    edges: tuple[tuple[str, str | None, str, str], ...] = (),
) -> QueryableCodeMap:
    files = {
        FileId(path): source_file(FileId(path))
        for path in paths
    }
    graph = DependencyGraph()
    for file_id in files:
        graph.add_node(file_id)
    for source, target, resolution, specifier in edges:
        graph.add_edge(
            FileId(source),
            FileId(target) if target is not None else None,
            resolution=resolution,
            specifier=ImportSpecifier(specifier),
        )
    return QueryableCodeMap(
        code_map=CodeMap(
            language="test",
            extraction=SourceExtraction(
                files=files,
                modules={source.module_id: file_id for file_id, source in files.items()},
                files_found=len(files),
                files_excluded=0,
            ),
            dependency_graph=graph,
        )
    )


def source_file(file_id: FileId) -> SourceFile:
    return SourceFile(
        file_id=file_id,
        module_id=ModuleId(file_id.rsplit(".", 1)[0]),
        imports=[],
        exports=[],
        classes=[],
        interfaces=[],
        types=[],
        abstract_classes=[],
        functions=[],
        values=[],
        callables=[],
        calls=[],
        line_count=1,
        code_line_count=1,
        public_symbol_count=0,
    )
