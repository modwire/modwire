from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from modwire import (
    EXTRACTION_SCHEMA_VERSION,
    ExtractionCache,
    LanguageInfo,
    RuntimeInfo,
    ShapeConfig,
    ShapeConfigError,
    ShapePolicyEvaluator,
    ShapeViolation,
    SourceRoots,
    UnsupportedLanguageError,
    __version__,
    build_dependency_graph,
    callable_report_entries,
    deserialize_code_map,
    discover_sources,
    extract_code,
    extraction_implementation_stamp,
    find_unused_exports,
    language,
    languages,
    normalize_source_id,
    render_callable_report,
    runtime_diagnostics,
    serialize_code_map,
    structured_callable_report,
    supported_languages,
    validate_shape_config,
)
from modwire.definitions import (
    SourceFile,
)
from modwire.extraction import CodeMap, ExtractionResult, ExtractionSummary
from modwire.extractors.base import ExtractorProcessError
from modwire.extractors.resources import extractor_script_path, read_extractor_script
from modwire.graph import DependencyGraph
from modwire.testing import (
    source_class,
    source_file as make_source_file,
    source_function,
    source_import as make_source_import,
    source_method,
    source_property,
)


APPS_DIR = Path(__file__).parent / "apps"


@dataclass(frozen=True)
class AppFixture:
    language: str
    root: Path
    runtime: str | None = None


@dataclass(frozen=True)
class ExtractorBatchFixture:
    language: str
    extension: str
    content: str
    batch_size_patch: str


class BuildDependencyGraphFunctionalTest(unittest.TestCase):
    def test_graph_builder_is_part_of_public_api(self) -> None:
        self.assertIsNotNone(build_dependency_graph)

    def test_extraction_package_keeps_public_api_imports(self) -> None:
        from modwire.extraction import CodeMap, ExtractionResult, extract_code

        self.assertIsNotNone(CodeMap)
        self.assertIsNotNone(ExtractionResult)
        self.assertIsNotNone(extract_code)

    def test_extractor_scripts_are_package_resources(self) -> None:
        for extractor_file in (
            "python_extractor.py",
            "typescript_extractor.js",
            "php_extractor.php",
        ):
            with self.subTest(extractor_file=extractor_file):
                with extractor_script_path(extractor_file) as script:
                    self.assertTrue(script.is_file())
                    self.assertEqual(script.name, extractor_file)
                self.assertTrue(read_extractor_script(extractor_file))

    def test_source_id_helpers_are_language_aware(self) -> None:
        self.assertEqual(supported_languages(), ("python", "typescript", "php"))
        self.assertEqual(normalize_source_id("python", r"src\app.py"), "src/app")
        self.assertEqual(normalize_source_id("typescript", "src/view.tsx"), "src/view")
        self.assertEqual(normalize_source_id("php", "src/Controller.php"), "src/Controller")

    def test_language_metadata_is_public_and_runtime_aware(self) -> None:
        infos = languages()

        self.assertEqual([info.name for info in infos], ["python", "typescript", "php"])
        self.assertTrue(all(isinstance(info, LanguageInfo) for info in infos))
        self.assertEqual(language("python").file_extensions, (".py",))
        self.assertEqual(language("typescript").command, "node")
        self.assertTrue(language("python").extractor_path.is_file())
        self.assertTrue(extraction_implementation_stamp("python"))
        self.assertIsInstance(runtime_diagnostics("python"), RuntimeInfo)
        self.assertTrue(runtime_diagnostics("python").available)
        self.assertTrue(runtime_diagnostics("python").command_path)
        self.assertIsInstance(__version__, str)
        self.assertEqual(EXTRACTION_SCHEMA_VERSION, 2)

    def test_unsupported_languages_raise_explicit_error(self) -> None:
        with self.assertRaises(UnsupportedLanguageError):
            language("ruby")

    def test_shape_policy_evaluator_reports_file_symbol_and_import_violations(self) -> None:
        file_under_test = make_source_file(
            imports=(
                make_source_import(
                    "shared",
                    is_aliased=True,
                    crossing_type="symbol",
                    join_key="shared",
                    uses_joined_import=False,
                ),
            ),
            classes=(
                source_class(
                    "Service",
                    methods=(
                        source_method(
                            "run",
                            line_count=12,
                            declared_args=3,
                            optional_args=1,
                        ),
                        source_method("save"),
                    ),
                    properties=(source_property("maybe", is_optional=True),),
                    line_count=25,
                ),
            ),
            functions=(
                source_function(
                    "build",
                    line_count=8,
                    declared_args=2,
                    optional_args=1,
                ),
            ),
            line_count=30,
            code_line_count=20,
            public_symbol_count=2,
        )
        code_map = CodeMap(
            graph=DependencyGraph(),
            extraction_result=ExtractionResult(
                files={"app": file_under_test},
                summary=ExtractionSummary(1, 1, 0),
            ),
            runtime_command="python",
        )

        violations = ShapePolicyEvaluator().evaluate(
            code_map,
            ShapeConfig(
                max_classes_per_file=-1,
                max_functions_per_file=-1,
                max_methods_per_class=1,
                max_declared_args=1,
                max_function_lines=5,
                max_method_lines=10,
                max_class_lines=20,
                allow_optional_function_args=False,
                allow_optional_method_args=False,
                allow_optional_class_properties=False,
                allow_import_aliases=False,
                allowed_import_crossing_types=("module",),
                require_joined_imports=True,
            ),
        )
        by_rule = {violation.rule_name: violation for violation in violations}

        self.assertTrue(all(isinstance(violation, ShapeViolation) for violation in violations))
        self.assertEqual(by_rule["max_methods_per_class"].actual, 2)
        self.assertEqual(by_rule["max_class_lines"].symbol_name, "Service")
        self.assertEqual(by_rule["max_function_lines"].symbol_name, "build")
        self.assertEqual(by_rule["max_method_lines"].symbol_name, "run")
        self.assertEqual(by_rule["allow_optional_function_args"].symbol_name, "build")
        self.assertEqual(by_rule["allow_optional_method_args"].symbol_name, "run")
        self.assertEqual(by_rule["allow_optional_class_properties"].symbol_name, "maybe")
        self.assertEqual(by_rule["allow_import_aliases"].symbol_name, "shared")
        self.assertEqual(by_rule["allowed_import_crossing_types"].actual, "symbol")
        self.assertEqual(by_rule["require_joined_imports"].symbol_name, "shared")
        self.assertEqual(
            by_rule["max_declared_args"].to_dict()["source_id"],
            "app",
        )

    def test_shape_config_validation_is_structured_and_accepts_dicts(self) -> None:
        sample = CodeMap(
            graph=DependencyGraph(),
            extraction_result=ExtractionResult(
                files={"app": make_source_file(functions=(source_function("run"),))},
                summary=ExtractionSummary(1, 1, 0),
            ),
            runtime_command="python",
        )

        violations = ShapePolicyEvaluator().evaluate(
            sample,
            {
                "max_functions_per_file": 0,
            },
        )

        self.assertEqual(violations[0].rule_name, "max_functions_per_file")
        self.assertEqual(validate_shape_config({}), ShapeConfig())
        with self.assertRaises(ShapeConfigError) as context:
            validate_shape_config({"max_functions_per_file": -2})

        payload = context.exception.to_dict()
        self.assertEqual(payload["error"], "invalid_shape_config")
        self.assertEqual(payload["issues"][0]["field"], "max_functions_per_file")

    def test_supported_apps_produce_the_same_dependency_graph(self) -> None:
        graphs_by_language: dict[str, set[tuple[str, str]]] = {}

        for fixture in app_fixtures():
            with self.subTest(language=fixture.language):
                if fixture.runtime is not None and shutil.which(fixture.runtime) is None:
                    self.skipTest(f"{fixture.runtime} runtime is not available")

                result = extract_code(
                    fixture.language,
                    fixture.root,
                    ("ignored/**",),
                )

                graphs_by_language[fixture.language] = internal_edges(result)

                self.assertEqual(
                    result.extraction_result.summary.files_found,
                    count_source_files(fixture.root),
                )
                self.assertEqual(
                    result.extraction_result.summary.files_excluded,
                    count_source_files(fixture.root / "ignored"),
                )
                self.assertEqual(
                    result.extraction_result.summary.files_checked,
                    len(result.extraction_result.files),
                )
                self.assert_has_nested_source_files(result)
                self.assert_has_classes_and_functions(result)
                self.assert_has_metrics(result)
                self.assert_has_import_barrier_metadata(fixture.language, result)
                self.assert_has_import_alias_metadata(fixture.language, result)
                self.assert_has_argument_count_metadata(fixture.language, result)
                self.assert_has_class_property_metadata(fixture.language, result)
                self.assert_has_visibility_metadata(fixture.language, result)

                if fixture.language == "typescript":
                    self.assert_scans_typescript_extensions(result)

        self.assertGreaterEqual(len(graphs_by_language), 2)
        self.assertEqual(len(set(map(frozenset, graphs_by_language.values()))), 1)

    def test_old_source_file_payloads_remain_valid(self) -> None:
        source_file = SourceFile.model_validate(
            {
                "imports": [
                    {
                        "path": "sample",
                        "is_relative": False,
                        "normalized_path": "sample",
                        "imported_name": "",
                        "is_aliased": False,
                        "crossing_type": "module",
                        "file_barrier_crossed": True,
                        "statement_id": 1,
                        "join_key": "",
                        "uses_joined_import": False,
                    }
                ],
                "classes": [],
                "functions": [],
                "line_count": 1,
                "code_line_count": 1,
                "public_symbol_count": 0,
            }
        )

        self.assertEqual(source_file.exports, [])
        self.assertEqual(source_file.imports[0].imported_symbols, [])
        self.assertEqual(source_file.values, [])
        self.assertEqual(source_file.callables, [])
        self.assertEqual(source_file.calls, [])

    def test_bare_directory_exclusions_are_recursive(self) -> None:
        result = extract_code("python", APPS_DIR / "python", ("ignored",))

        self.assertEqual(
            result.extraction_result.summary.files_excluded,
            count_source_files(APPS_DIR / "python" / "ignored"),
        )
        self.assertTrue(
            all(
                not source_id.startswith("ignored/")
                for source_id in result.extraction_result.files
            )
        )

    def test_excluded_directories_are_pruned_before_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("app.py").write_text("def run():\n    pass\n", encoding="utf-8")
            ignored = root / "ignored"
            ignored.mkdir()
            ignored.joinpath("generated.py").write_text(
                "def generated():\n    pass\n",
                encoding="utf-8",
            )

            real_iterdir = Path.iterdir

            def guarded_iterdir(path: Path):
                if path == ignored:
                    raise AssertionError("ignored directory should be pruned")
                return real_iterdir(path)

            with patch.object(Path, "iterdir", guarded_iterdir):
                result = extract_code("python", root, ("ignored/**",))

        self.assertEqual(set(result.extraction_result.files), {"app"})
        self.assertEqual(result.extraction_result.summary.files_excluded, 1)

    def test_file_level_exclusion_summary_remains_sensible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("app.py").write_text("def run():\n    pass\n", encoding="utf-8")
            root.joinpath("generated.py").write_text(
                "def generated():\n    pass\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ("generated.py",))

        self.assertEqual(result.extraction_result.summary.files_found, 2)
        self.assertEqual(result.extraction_result.summary.files_excluded, 1)
        self.assertEqual(set(result.extraction_result.files), {"app"})

    def test_discover_sources_exposes_manifest_with_extraction_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("app.py").write_text("def run():\n    pass\n", encoding="utf-8")
            ignored = root / "ignored"
            ignored.mkdir()
            ignored.joinpath("generated.py").write_text(
                "def generated():\n    pass\n",
                encoding="utf-8",
            )

            manifest = discover_sources("python", root, ("ignored/**",))

        self.assertEqual(manifest.language, "python")
        self.assertEqual(manifest.files_found, 2)
        self.assertEqual(manifest.files_checked, 1)
        self.assertEqual(manifest.files_excluded, 1)
        self.assertEqual([entry.source_id for entry in manifest.entries], ["app"])
        self.assertEqual(manifest.entries[0].size, len("def run():\n    pass\n"))
        self.assertTrue(manifest.extractor_path.name.endswith("_extractor.py"))
        self.assertTrue(manifest.fingerprint())

    def test_code_map_serialization_round_trips_graph_and_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("dep.py").write_text("class Dep:\n    pass\n", encoding="utf-8")
            root.joinpath("app.py").write_text(
                "from dep import Dep\n\n"
                "def run():\n"
                "    return Dep()\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        loaded = deserialize_code_map(serialize_code_map(result))

        self.assertEqual(
            loaded.extraction_result.summary,
            result.extraction_result.summary,
        )
        self.assertEqual(
            set(loaded.extraction_result.files),
            set(result.extraction_result.files),
        )
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in loaded.graph.edges],
            [(edge.from_id, edge.to_id) for edge in result.graph.edges],
        )
        self.assertEqual(
            loaded.graph.outgoing("app"),
            result.graph.outgoing("app"),
        )
        self.assertEqual(
            loaded.graph.incoming("dep"),
            result.graph.incoming("dep"),
        )

    def test_code_map_deserializes_v1_payloads_without_callable_fields(self) -> None:
        loaded = deserialize_code_map(
            {
                "schema_version": 1,
                "runtime_command": "python",
                "extraction_result": {
                    "summary": {
                        "files_found": 1,
                        "files_checked": 1,
                        "files_excluded": 0,
                    },
                    "files": {"app": source_file_payload()},
                },
                "graph": {
                    "nodes": {"app": {"id": "app", "kind": "file"}},
                    "edges": [],
                },
            }
        )

        source_file = loaded.extraction_result.files["app"]
        self.assertEqual(source_file.values, [])
        self.assertEqual(source_file.callables, [])
        self.assertEqual(source_file.calls, [])

    def test_graph_exposes_common_transform_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("dep.py").write_text("class Dep:\n    pass\n", encoding="utf-8")
            root.joinpath("app.py").write_text(
                "from dep import Dep\n"
                "import json\n\n"
                "def run():\n"
                "    return Dep(), json.dumps({})\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        graph = result.graph

        self.assertTrue(graph.has_node("app"))
        self.assertEqual([edge.from_id for edge in graph.incoming("dep")], ["app"])
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in graph.edges_between("app", "dep")],
            [("app", "dep")],
        )
        self.assertEqual(
            [node.id for node in graph.sorted_nodes()],
            ["app", "dep", "json"],
        )
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in result.tracked_edges()],
            [("app", "dep")],
        )
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in result.external_edges()],
            [("app", "json")],
        )

        tracked = result.tracked_only()
        self.assertEqual(set(tracked.graph.nodes), {"app", "dep"})
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in tracked.graph.edges],
            [("app", "dep")],
        )

        dep_only = result.subgraph(("dep",))
        self.assertEqual(set(dep_only.extraction_result.files), {"dep"})
        self.assertEqual(dep_only.graph.edges, [])

    def test_callable_graph_extracts_values_callables_and_calls_across_languages(self) -> None:
        fixtures = [
            (
                "python",
                "sample.py",
                None,
                "THRESHOLD = 1\n"
                "handler = lambda value: helper(value)\n\n"
                "def helper(value):\n"
                "    return str(value)\n\n"
                "class Service:\n"
                "    def run(self, value):\n"
                "        return helper(value)\n\n"
                "def dispatch(items):\n"
                "    return list(map(lambda item: helper(item), items))\n\n"
                "def external_call():\n"
                "    return missing()\n",
            ),
            (
                "typescript",
                "sample.ts",
                "node",
                "const threshold = 1;\n"
                "const handler = (value) => helper(value);\n\n"
                "function helper(value) { return String(value); }\n\n"
                "class Service {\n"
                "    run(value) { return helper(value); }\n"
                "}\n\n"
                "function dispatch(items) {\n"
                "    return items.map(item => helper(item));\n"
                "}\n\n"
                "function externalCall() { return missing(); }\n",
            ),
            (
                "php",
                "sample.php",
                "php",
                "<?php\n"
                "const THRESHOLD = 1;\n"
                "$handler = function ($value) { return helper($value); };\n\n"
                "function helper($value) { return (string) $value; }\n\n"
                "class Service {\n"
                "    public function run($value) { return helper($value); }\n"
                "}\n\n"
                "function dispatch($items) {\n"
                "    return array_map(fn ($item) => helper($item), $items);\n"
                "}\n\n"
                "function externalCall() { return missing(); }\n",
            ),
        ]

        for language_name, filename, runtime, source in fixtures:
            with self.subTest(language=language_name):
                if runtime is not None and shutil.which(runtime) is None:
                    self.skipTest(f"{runtime} runtime is not available")
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    root.joinpath(filename).write_text(source, encoding="utf-8")

                    result = extract_code(language_name, root, ())

                source_file = result.extraction_result.files["sample"]
                values_by_name = {value.name: value for value in source_file.values}
                callables_by_id = {
                    source_callable.id: source_callable
                    for source_callable in source_file.callables
                }
                helper_id = "sample::helper"
                method_id = "sample::Service.run"
                handler_id = "sample::handler"

                self.assertIn(helper_id, callables_by_id)
                self.assertEqual(callables_by_id[helper_id].kind, "function")
                self.assertIn(method_id, callables_by_id)
                self.assertEqual(callables_by_id[method_id].kind, "method")
                self.assertIn(handler_id, callables_by_id)
                self.assertEqual(callables_by_id[handler_id].kind, "callable_value")
                self.assertTrue(
                    any(
                        source_callable.kind == "anonymous"
                        for source_callable in source_file.callables
                    )
                )
                self.assertTrue(
                    any(value.value_kind != "callable" for value in source_file.values)
                )
                self.assertTrue(
                    any(value.value_kind == "callable" for value in values_by_name.values())
                )

                helper_calls = [
                    source_call
                    for source_call in source_file.calls
                    if source_call.target_name == "helper"
                ]
                self.assertTrue(
                    any(
                        source_call.source_callable_id == handler_id
                        and source_call.target_callable_id == helper_id
                        and source_call.resolution == "resolved"
                        for source_call in helper_calls
                    )
                )
                self.assertTrue(
                    any(
                        source_call.source_callable_id == method_id
                        and source_call.target_callable_id == helper_id
                        and source_call.resolution == "resolved"
                        for source_call in helper_calls
                    )
                )
                self.assertTrue(
                    any(
                        callables_by_id[source_call.source_callable_id].kind == "anonymous"
                        and source_call.target_callable_id == helper_id
                        for source_call in helper_calls
                    )
                )
                self.assertTrue(
                    any(
                        source_call.target_name == "missing"
                        and source_call.target_callable_id == ""
                        and source_call.resolution == "unresolved"
                        for source_call in source_file.calls
                    )
                )

                graph = result.callable_graph()
                self.assertEqual(result.callable(helper_id).name, "helper")
                self.assertIn(handler_id, result.callable_ids())
                self.assertTrue(
                    any(
                        source_call.target_callable_id == helper_id
                        for source_call in result.calls_from(handler_id)
                    )
                )
                self.assertTrue(
                    any(
                        source_call.source_callable_id == method_id
                        for source_call in result.calls_to(helper_id)
                    )
                )
                self.assertIn(
                    (handler_id, helper_id),
                    {(edge.from_id, edge.to_id) for edge in graph.edges},
                )

    def test_callable_report_lists_calls_and_callers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("app.py").write_text(
                "handler = lambda value: helper(value)\n\n"
                "def helper(value):\n"
                "    return value\n\n"
                "def run():\n"
                "    handler(1)\n"
                "    missing()\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        entries = callable_report_entries(result)
        structured = structured_callable_report(result)
        rendered = render_callable_report(result, path_display=lambda path: f"<{path}>")

        self.assertEqual(
            [entry.source_callable.qualified_name for entry in entries],
            ["handler", "helper", "run"],
        )
        self.assertEqual(structured[0]["callable"]["qualified_name"], "handler")
        self.assertIn("Callable Report", rendered)
        self.assertIn("## <app>", rendered)
        self.assertIn("- handler [callable_value] lines 1-1", rendered)
        self.assertIn("helper -> helper at <app>:1 (resolved)", rendered)
        self.assertIn("handler -> handler at <app>:7 (resolved)", rendered)
        self.assertIn("missing -> missing at <app>:8 (unresolved)", rendered)
        self.assertIn("handler at <app>:1", rendered)

    def test_testing_factories_build_minimal_code_maps(self) -> None:
        from modwire.testing import (
            code_map,
            dependency_graph,
            source_class,
            source_file as make_source_file,
            source_function,
            source_import as make_source_import,
            source_method,
            source_property,
        )

        sample = code_map(
            files=("app", "dep"),
            edges=(("app", "dep"),),
        )
        graph = dependency_graph(edges=(("app", "dep"),))
        imported = make_source_import("dep", is_aliased=True)
        file = make_source_file(
            imports=(imported,),
            classes=(
                source_class(
                    "Service",
                    methods=(source_method("run", declared_args=1),),
                    properties=(source_property("maybe", is_optional=True),),
                ),
            ),
            functions=(source_function("build", optional_args=1),),
        )

        self.assertEqual(set(sample.extraction_result.files), {"app", "dep"})
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in sample.graph.edges],
            [("app", "dep")],
        )
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in graph.edges],
            [("app", "dep")],
        )
        self.assertTrue(file.imports[0].is_aliased)
        self.assertEqual(file.classes[0].methods[0].declared_args, 1)
        self.assertTrue(file.classes[0].properties[0].is_optional)
        self.assertEqual(file.functions[0].optional_args, 1)

    def test_extraction_cache_reuses_serialized_code_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache_root = root / ".modwire-cache"
            root.joinpath("one.py").write_text("def one():\n    pass\n", encoding="utf-8")
            root.joinpath("two.py").write_text("def two():\n    pass\n", encoding="utf-8")

            with patch("modwire.extractors.base.run") as run_mock:
                run_mock.side_effect = fake_batch_run
                first = extract_code(
                    "python",
                    root,
                    (),
                    cache=ExtractionCache(cache_root),
                )
                second = extract_code(
                    "python",
                    root,
                    (),
                    cache=ExtractionCache(cache_root),
                )

        self.assertEqual(first.cache_status, "miss")
        self.assertEqual(second.cache_status, "hit")
        self.assertEqual(first.cache_key, second.cache_key)
        self.assertEqual(run_mock.call_count, 1)
        self.assertEqual(set(second.extraction_result.files), {"one", "two"})

    def test_extraction_can_return_workspace_relative_source_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            source_root = workspace / "src" / "app" / "features"
            source_root.joinpath("application").mkdir(parents=True)
            source_root.joinpath("domain").mkdir()
            source_root.joinpath("generated").mkdir()
            source_root.joinpath("domain", "model.py").write_text(
                "class Model:\n    pass\n",
                encoding="utf-8",
            )
            source_root.joinpath("application", "use_case.py").write_text(
                "from ..domain.model import Model\n\n"
                "def run():\n"
                "    return Model()\n",
                encoding="utf-8",
            )
            source_root.joinpath("generated", "ignored.py").write_text(
                "def ignored():\n    pass\n",
                encoding="utf-8",
            )

            result = extract_code(
                "python",
                source_root,
                ("src/app/features/generated/**",),
                source_roots=SourceRoots(
                    workspace_root=workspace,
                    source_id_mode="relative_to_workspace_root",
                ),
            )
            manifest = discover_sources(
                "python",
                source_root,
                ("src/app/features/generated/**",),
                source_roots=SourceRoots(
                    workspace_root=workspace,
                    source_id_mode="relative_to_workspace_root",
                ),
            )

        self.assertEqual(
            set(result.extraction_result.files),
            {
                "src/app/features/application/use_case",
                "src/app/features/domain/model",
            },
        )
        self.assertIn(
            ("src/app/features/application/use_case", "src/app/features/domain/model"),
            {(edge.from_id, edge.to_id) for edge in result.graph.edges},
        )
        self.assertEqual(result.extraction_result.summary.files_found, 3)
        self.assertEqual(result.extraction_result.summary.files_excluded, 1)
        self.assertEqual(manifest.exclusions, ("generated/**",))
        self.assertEqual(
            [entry.source_id for entry in manifest.entries],
            [
                "src/app/features/application/use_case",
                "src/app/features/domain/model",
            ],
        )

    def test_extraction_can_use_explicit_logical_source_id_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            source_root = workspace / "packages" / "sales"
            source_root.mkdir(parents=True)
            source_root.joinpath("service.py").write_text(
                "def run():\n    pass\n",
                encoding="utf-8",
            )

            result = extract_code(
                "python",
                source_root,
                (),
                source_roots=SourceRoots(
                    workspace_root=workspace,
                    source_id_root="logical/sales",
                ),
            )
            manifest = discover_sources(
                "python",
                source_root,
                (),
                source_roots=SourceRoots(
                    workspace_root=workspace,
                    source_id_root="logical/sales",
                ),
            )

        self.assertEqual(set(result.extraction_result.files), {"logical/sales/service"})
        self.assertEqual(manifest.source_id_root, "logical/sales")
        self.assertEqual(manifest.source_id_prefix, "logical/sales")

    def test_python_batch_output_equals_single_file_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.py"
            source.write_text(
                "class User:\n"
                "    pass\n\n"
                "def build_user():\n"
                "    return User()\n",
                encoding="utf-8",
            )

            script = extractor_script("python_extractor.py")
            single = extractor_output(
                [sys.executable, str(script), str(source), str(root)]
            )
            batch = extractor_output(
                [sys.executable, str(script), "--batch", str(root)],
                {"sample": str(source)},
            )

        self.assertEqual(batch["sample"], single)

    def test_typescript_batch_output_equals_single_file_output(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.ts"
            source.write_text(
                "export class User {}\n"
                "export function buildUser(): User { return new User(); }\n",
                encoding="utf-8",
            )

            script = extractor_script("typescript_extractor.js")
            single = extractor_output(["node", str(script), str(source), str(root)])
            batch = extractor_output(
                ["node", str(script), "--batch", str(root)],
                {"sample": str(source)},
            )

        self.assertEqual(batch["sample"], single)

    def test_extractor_failure_includes_subprocess_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("app.py").write_text("def run():\n    pass\n", encoding="utf-8")
            failure = subprocess.CalledProcessError(
                1,
                ["python", "python_extractor.py", "--batch", str(root)],
                output="before\nlast stdout line\n",
                stderr="before\nSyntaxError: broken fixture\n",
            )

            with patch("modwire.extractors.base.run", side_effect=failure):
                with self.assertRaises(ExtractorProcessError) as context:
                    extract_code("python", root, ())

        message = str(context.exception)
        self.assertIn("Extractor subprocess failed.", message)
        self.assertIn("exit code: 1", message)
        self.assertIn("language: python", message)
        self.assertIn(f"source root: {root.resolve()}", message)
        self.assertIn("files: 1", message)
        self.assertIn("stdout tail:", message)
        self.assertIn("last stdout line", message)
        self.assertIn("stderr tail:", message)
        self.assertIn("SyntaxError: broken fixture", message)

    def test_extractors_use_one_subprocess_for_inputs_within_batch_size(self) -> None:
        for fixture in extractor_batch_fixtures():
            with self.subTest(language=fixture.language):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    for source_id in ("one", "two"):
                        root.joinpath(f"{source_id}{fixture.extension}").write_text(
                            fixture.content,
                            encoding="utf-8",
                        )

                    with patch("modwire.extractors.base.run") as run_mock:
                        run_mock.side_effect = fake_batch_run
                        result = extract_code(fixture.language, root, ())

                self.assertEqual(run_mock.call_count, 1)
                self.assertEqual(set(result.extraction_result.files), {"one", "two"})
                self.assertIn("--batch", run_mock.call_args.args[0])

    def test_extractors_batch_subprocesses_to_limit_json_payload_size(self) -> None:
        for fixture in extractor_batch_fixtures():
            with self.subTest(language=fixture.language):
                with tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    for index in range(5):
                        root.joinpath(f"file_{index}{fixture.extension}").write_text(
                            fixture.content,
                            encoding="utf-8",
                        )

                    with (
                        patch(fixture.batch_size_patch, 2),
                        patch("modwire.extractors.base.run") as run_mock,
                    ):
                        run_mock.side_effect = fake_batch_run
                        result = extract_code(fixture.language, root, ())

                self.assertEqual(run_mock.call_count, 3)
                self.assertEqual(
                    set(result.extraction_result.files),
                    {f"file_{index}" for index in range(5)},
                )
                self.assertEqual(batch_input_sizes(run_mock), [2, 2, 1])
                self.assertTrue(
                    all("--batch" in call.args[0] for call in run_mock.call_args_list)
                )

    def test_python_visibility_distinguishes_accessibility_from_intent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("sample.py").write_text(
                "class _Internal:\n"
                "    def _guarded(self):\n"
                "        pass\n"
                "    def __hidden(self):\n"
                "        pass\n"
                "    def __str__(self):\n"
                "        return 'internal'\n\n"
                "def _helper():\n"
                "    pass\n\n"
                "def __secret():\n"
                "    pass\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        self.assertEqual(
            class_visibility(result, "sample", "_Internal"),
            ("public", "protected"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "_Internal", "_guarded"),
            ("public", "protected"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "_Internal", "__hidden"),
            ("public", "private"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "_Internal", "__str__"),
            ("public", "public"),
        )
        self.assertEqual(
            function_visibility(result, "sample", "_helper"),
            ("public", "protected"),
        )
        self.assertEqual(
            function_visibility(result, "sample", "__secret"),
            ("public", "private"),
        )

    def test_typescript_visibility_uses_exports_and_member_modifiers(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("sample.ts").write_text(
                "export class PublicUser {\n"
                "    public open(): void {}\n"
                "    protected guarded(): void {}\n"
                "    private hidden(): void {}\n"
                "    #hashed(): void {}\n"
                "    _convention(): void {}\n"
                "}\n\n"
                "class LocalUser {}\n\n"
                "export function run(): void {}\n"
                "function local(): void {}\n",
                encoding="utf-8",
            )

            result = extract_code("typescript", root, ())

        self.assertEqual(
            class_visibility(result, "sample", "PublicUser"),
            ("public", "public"),
        )
        self.assertEqual(
            class_visibility(result, "sample", "LocalUser"),
            ("private", "private"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "open"),
            ("public", "public"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "guarded"),
            ("protected", "protected"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "hidden"),
            ("private", "private"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "#hashed"),
            ("private", "private"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "_convention"),
            ("public", "protected"),
        )
        self.assertEqual(
            function_visibility(result, "sample", "run"),
            ("public", "public"),
        )
        self.assertEqual(
            function_visibility(result, "sample", "local"),
            ("private", "private"),
        )

    def test_php_visibility_uses_method_modifiers(self) -> None:
        if shutil.which("php") is None:
            self.skipTest("php runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("sample.php").write_text(
                "<?php\n"
                "final class PublicUser\n"
                "{\n"
                "    public function open(): void {}\n"
                "    protected function guarded(): void {}\n"
                "    private function hidden(): void {}\n"
                "    public function _convention(): void {}\n"
                "    public function __construct() {}\n"
                "}\n\n"
                "function _helper(): void {}\n",
                encoding="utf-8",
            )

            result = extract_code("php", root, ())

        self.assertEqual(
            class_visibility(result, "sample", "PublicUser"),
            ("public", "public"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "open"),
            ("public", "public"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "guarded"),
            ("protected", "protected"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "hidden"),
            ("private", "private"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "_convention"),
            ("public", "protected"),
        )
        self.assertEqual(
            method_visibility(result, "sample", "PublicUser", "__construct"),
            ("public", "public"),
        )
        self.assertEqual(
            function_visibility(result, "sample", "_helper"),
            ("public", "protected"),
        )

    def test_python_extracts_abstract_classes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("sample.py").write_text(
                "from abc import ABC, abstractmethod\n\n"
                "class Repository(ABC):\n"
                "    enabled: bool\n\n"
                "    @abstractmethod\n"
                "    def load(self, user_id: str):\n"
                "        raise NotImplementedError\n\n"
                "    def save(self, user_id: str | None = None):\n"
                "        return user_id\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        source_file = result.extraction_result.files["sample"]
        self.assertEqual(
            [abstract.name for abstract in source_file.abstract_classes],
            ["Repository"],
        )
        self.assertEqual(source_file.classes, [])
        abstract_class = source_file.abstract_classes[0]
        self.assertEqual(
            [method.name for method in abstract_class.abstract_methods],
            ["load"],
        )
        self.assertEqual(
            [method.name for method in abstract_class.concrete_methods],
            ["save"],
        )
        self.assertEqual(
            {
                property.name: property.is_optional
                for property in abstract_class.properties
            },
            {"enabled": False},
        )
        self.assertEqual(source_file.interfaces, [])
        self.assertEqual(source_file.types, [])

    def test_typescript_extracts_interfaces_types_and_abstract_classes(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("sample.ts").write_text(
                "export interface UserPort extends Runnable {\n"
                "    (id: string, retry?: boolean): User;\n"
                "    new (seed?: User): UserPort;\n"
                "    [key: string]: User;\n"
                "    user?: User;\n"
                "    load(id: string, retry?: boolean): User;\n"
                "}\n\n"
                "export type UserPayload = {\n"
                "    (id: string): User;\n"
                "    [key: string]: User;\n"
                "    id: string;\n"
                "    owner?: User;\n"
                "} & Audited;\n\n"
                "export abstract class BaseRepository {\n"
                "    protected cache?: User;\n"
                "    abstract load(id: string): User;\n"
                "    save(user?: User): void {}\n"
                "}\n",
                encoding="utf-8",
            )

            result = extract_code("typescript", root, ())

        source_file = result.extraction_result.files["sample"]
        self.assertEqual(source_file.classes, [])
        self.assertEqual(
            [interface.name for interface in source_file.interfaces],
            ["UserPort"],
        )
        interface = source_file.interfaces[0]
        self.assertEqual([method.name for method in interface.methods], ["load"])
        self.assertEqual(
            {property.name: property.is_optional for property in interface.properties},
            {"user": True},
        )
        self.assertEqual(
            {
                (signature.kind, signature.declared_args, signature.optional_args)
                for signature in interface.signatures
            },
            {
                ("call", 2, 1),
                ("construct", 1, 1),
                ("index", 1, 0),
            },
        )

        self.assertEqual(
            [source_type.name for source_type in source_file.types],
            ["UserPayload"],
        )
        source_type = source_file.types[0]
        self.assertEqual(
            {
                property.name: property.is_optional
                for property in source_type.properties
            },
            {"id": False, "owner": True},
        )
        self.assertEqual(
            {
                (signature.kind, signature.declared_args, signature.optional_args)
                for signature in source_type.signatures
            },
            {
                ("call", 1, 0),
                ("index", 1, 0),
            },
        )

        self.assertEqual(
            [abstract.name for abstract in source_file.abstract_classes],
            ["BaseRepository"],
        )
        abstract_class = source_file.abstract_classes[0]
        self.assertEqual(
            [method.name for method in abstract_class.abstract_methods],
            ["load"],
        )
        self.assertEqual(
            [method.name for method in abstract_class.concrete_methods],
            ["save"],
        )
        self.assertEqual(
            {
                property.name: property.is_optional
                for property in abstract_class.properties
            },
            {"cache": True},
        )

    def test_php_extracts_interfaces_and_abstract_classes(self) -> None:
        if shutil.which("php") is None:
            self.skipTest("php runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("sample.php").write_text(
                "<?php\n"
                "interface UserPort extends Runnable\n"
                "{\n"
                "    public const KIND = 'user';\n"
                "    public function load(string $id): User;\n"
                "}\n\n"
                "abstract class BaseRepository\n"
                "{\n"
                "    protected ?string $cache;\n"
                "    abstract protected function load(string $id): User;\n"
                "    public function save(?User $user = null): void {}\n"
                "}\n",
                encoding="utf-8",
            )

            result = extract_code("php", root, ())

        source_file = result.extraction_result.files["sample"]
        self.assertEqual(source_file.classes, [])
        self.assertEqual(
            [interface.name for interface in source_file.interfaces],
            ["UserPort"],
        )
        interface = source_file.interfaces[0]
        self.assertEqual([method.name for method in interface.methods], ["load"])
        self.assertEqual(interface.signatures, [])
        self.assertEqual(source_file.types, [])

        self.assertEqual(
            [abstract.name for abstract in source_file.abstract_classes],
            ["BaseRepository"],
        )
        abstract_class = source_file.abstract_classes[0]
        self.assertEqual(
            [method.name for method in abstract_class.abstract_methods],
            ["load"],
        )
        self.assertEqual(
            [method.name for method in abstract_class.concrete_methods],
            ["save"],
        )
        self.assertEqual(
            {property.name: property.is_optional for property in abstract_class.properties},
            {"cache": True},
        )

    def test_python_absolute_package_imports_resolve_to_known_init_files_without_source_root_assumptions(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            package_dir = root / "packages" / "acme" / "tools"
            package_dir.mkdir(parents=True)
            package_dir.joinpath("__init__.py").write_text(
                "class Tool:\n    pass\n",
                encoding="utf-8",
            )
            service_dir = root / "services"
            service_dir.mkdir()
            service_dir.joinpath("report.py").write_text(
                "from acme.tools import Tool\n\n"
                "class Report:\n"
                "    tool = Tool\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        self.assertIn(
            ("services/report", "packages/acme/tools/__init__"),
            {
                (edge.from_id, edge.to_id)
                for edge in result.graph.edges
            },
        )

    def test_python_from_import_can_target_a_module_without_symbol_crossing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "src"
            source_dir.mkdir()
            source_dir.joinpath("service.py").write_text(
                "class Service:\n"
                "    pass\n",
                encoding="utf-8",
            )
            source_dir.joinpath("consumer.py").write_text(
                "from src import service\n\n"
                "def build():\n"
                "    return service.Service()\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        imports = result.extraction_result.files["src/consumer"].imports
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0].normalized_path, "src/service")
        self.assertEqual(imports[0].crossing_type, "module")
        self.assertTrue(imports[0].file_barrier_crossed)

    def test_python_import_metadata_distinguishes_joined_and_separate_parent_imports(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            shared_dir = root / "enclosure" / "shared"
            shared_dir.mkdir(parents=True)
            shared_dir.joinpath("__init__.py").write_text("", encoding="utf-8")
            shared_dir.joinpath("naming.py").write_text("", encoding="utf-8")
            shared_dir.joinpath("paths.py").write_text("", encoding="utf-8")
            feature_dir = root / "src" / "feature"
            feature_dir.mkdir(parents=True)
            feature_dir.joinpath("__init__.py").write_text(
                "from . import domain\n"
                "from . import ui\n",
                encoding="utf-8",
            )
            feature_dir.joinpath("domain.py").write_text("", encoding="utf-8")
            feature_dir.joinpath("ui.py").write_text("", encoding="utf-8")
            root.joinpath("separate.py").write_text(
                "import enclosure.shared.naming\n"
                "import enclosure.shared.paths\n",
                encoding="utf-8",
            )
            root.joinpath("joined.py").write_text(
                "from enclosure.shared import naming, paths\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        separate_imports = result.extraction_result.files["separate"].imports
        self.assertEqual(
            {source_import.join_key for source_import in separate_imports},
            {"enclosure/shared"},
        )
        self.assertEqual(
            len({source_import.statement_id for source_import in separate_imports}),
            2,
        )
        self.assertFalse(
            any(source_import.uses_joined_import for source_import in separate_imports)
        )

        joined_imports = result.extraction_result.files["joined"].imports
        self.assertEqual(
            {source_import.join_key for source_import in joined_imports},
            {"enclosure/shared"},
        )
        self.assertEqual(
            len({source_import.statement_id for source_import in joined_imports}),
            1,
        )
        self.assertTrue(
            all(source_import.uses_joined_import for source_import in joined_imports)
        )

        relative_imports = result.extraction_result.files["src/feature/__init__"].imports
        self.assertEqual(
            {source_import.join_key for source_import in relative_imports},
            {"src/feature"},
        )
        self.assertEqual(
            len({source_import.statement_id for source_import in relative_imports}),
            2,
        )

    def test_typescript_import_metadata_tracks_joinable_static_imports(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            domain_dir = root / "src" / "domain"
            domain_dir.mkdir(parents=True)
            domain_dir.joinpath("user.ts").write_text(
                "export class User {}\n"
                "export function buildUser(): User { return new User(); }\n",
                encoding="utf-8",
            )
            interfaces_dir = root / "src" / "interfaces"
            interfaces_dir.mkdir(parents=True)
            interfaces_dir.joinpath("controller.ts").write_text(
                "import { User } from '../domain/user';\n"
                "import { buildUser } from '../domain/user';\n"
                "import * as userModule from '../domain/user';\n"
                "import '../domain/user';\n"
                "const user = require('../domain/user');\n",
                encoding="utf-8",
            )

            result = extract_code("typescript", root, ())

        imports = result.extraction_result.files["src/interfaces/controller"].imports
        joinable_imports = [
            source_import for source_import in imports if source_import.join_key
        ]
        self.assertEqual(len(joinable_imports), 2)
        self.assertEqual(
            {source_import.join_key for source_import in joinable_imports},
            {"src/domain/user"},
        )
        self.assertEqual(
            len({source_import.statement_id for source_import in joinable_imports}),
            2,
        )
        self.assertTrue(
            all(source_import.uses_joined_import for source_import in joinable_imports)
        )

    def test_php_import_metadata_parses_grouped_use_imports(self) -> None:
        if shutil.which("php") is None:
            self.skipTest("php runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_dir = root / "src" / "domain" / "model"
            model_dir.mkdir(parents=True)
            model_dir.joinpath("user.php").write_text(
                "<?php\nnamespace App\\Domain\\Model;\nclass User {}\n",
                encoding="utf-8",
            )
            model_dir.joinpath("profile.php").write_text(
                "<?php\nnamespace App\\Domain\\Model;\nclass Profile {}\n",
                encoding="utf-8",
            )
            controller_dir = root / "src" / "interfaces"
            controller_dir.mkdir(parents=True)
            controller_dir.joinpath("separate.php").write_text(
                "<?php\n"
                "use App\\Domain\\Model\\User;\n"
                "use App\\Domain\\Model\\Profile;\n",
                encoding="utf-8",
            )
            controller_dir.joinpath("grouped.php").write_text(
                "<?php\n"
                "use App\\Domain\\Model\\{User, Profile};\n",
                encoding="utf-8",
            )

            result = extract_code("php", root, ())

        separate_imports = result.extraction_result.files[
            "src/interfaces/separate"
        ].imports
        self.assertEqual(
            {source_import.join_key for source_import in separate_imports},
            {"src/domain/model"},
        )
        self.assertEqual(
            len({source_import.statement_id for source_import in separate_imports}),
            2,
        )
        self.assertFalse(
            any(source_import.uses_joined_import for source_import in separate_imports)
        )

        grouped_imports = result.extraction_result.files[
            "src/interfaces/grouped"
        ].imports
        self.assertEqual(
            {source_import.join_key for source_import in grouped_imports},
            {"src/domain/model"},
        )
        self.assertEqual(
            len({source_import.statement_id for source_import in grouped_imports}),
            1,
        )
        self.assertTrue(
            all(source_import.uses_joined_import for source_import in grouped_imports)
        )

    def test_php_absolute_imports_resolve_without_app_or_source_root_assumptions(
        self,
    ) -> None:
        if shutil.which("php") is None:
            self.skipTest("php runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_dir = root / "packages" / "acme" / "domain" / "model"
            model_dir.mkdir(parents=True)
            model_dir.joinpath("user.php").write_text(
                "<?php\n\n"
                "namespace Acme\\Domain\\Model;\n\n"
                "class User {}\n",
                encoding="utf-8",
            )
            controller_dir = root / "web"
            controller_dir.mkdir()
            controller_dir.joinpath("controller.php").write_text(
                "<?php\n\n"
                "namespace Acme\\Web;\n\n"
                "use Acme\\Domain\\Model\\User;\n\n"
                "class Controller\n"
                "{\n"
                "    public function handle(User $user): void {}\n"
                "}\n",
                encoding="utf-8",
            )

            result = extract_code("php", root, ())

        self.assertIn(
            ("web/controller", "packages/acme/domain/model/user"),
            {
                (edge.from_id, edge.to_id)
                for edge in result.graph.edges
            },
        )

    def test_python_exports_and_unused_exports_follow_all_reexports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("user.py").write_text(
                "class User:\n"
                "    pass\n\n"
                "class UnusedUser:\n"
                "    pass\n",
                encoding="utf-8",
            )
            root.joinpath("api.py").write_text(
                "from .user import User\n\n"
                "__all__ = ['User']\n",
                encoding="utf-8",
            )
            root.joinpath("consumer.py").write_text(
                "from api import User\n",
                encoding="utf-8",
            )

            result = extract_code("python", root, ())

        api_exports = result.extraction_result.files["api"].exports
        self.assertIn(
            ("api", "module", "module"),
            {
                (source_export.name, source_export.kind, source_export.crossing_type)
                for source_export in api_exports
            },
        )
        self.assertIn(
            ("User", "unknown", True, "user"),
            {
                (
                    source_export.name,
                    source_export.kind,
                    source_export.is_reexport,
                    source_export.normalized_path,
                )
                for source_export in api_exports
            },
        )

        unused = {
            (source_export.source_id, source_export.name)
            for source_export in find_unused_exports(result.extraction_result)
        }
        self.assertNotIn(("api", "User"), unused)
        self.assertNotIn(("user", "User"), unused)
        self.assertIn(("user", "UnusedUser"), unused)

    def test_typescript_exports_reexports_and_import_symbols_are_additive(self) -> None:
        if shutil.which("node") is None:
            self.skipTest("node runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            root.joinpath("lib.ts").write_text(
                "export class User {}\n"
                "export function unusedUser(): void {}\n",
                encoding="utf-8",
            )
            root.joinpath("extra.ts").write_text(
                "export function helper(): void {}\n"
                "export function unusedHelper(): void {}\n",
                encoding="utf-8",
            )
            root.joinpath("barrel.ts").write_text(
                "export { User } from './lib';\n"
                "export * from './extra';\n",
                encoding="utf-8",
            )
            root.joinpath("consumer.ts").write_text(
                "import { User, helper } from './barrel';\n"
                "new User();\n"
                "helper();\n",
                encoding="utf-8",
            )

            result = extract_code("typescript", root, ())

        consumer_import = result.extraction_result.files["consumer"].imports[0]
        self.assertEqual(consumer_import.imported_name, "")
        self.assertEqual(
            [symbol.name for symbol in consumer_import.imported_symbols],
            ["User", "helper"],
        )
        unused = {
            (source_export.source_id, source_export.name)
            for source_export in find_unused_exports(result.extraction_result)
        }
        self.assertNotIn(("barrel", "User"), unused)
        self.assertNotIn(("lib", "User"), unused)
        self.assertNotIn(("extra", "helper"), unused)
        self.assertIn(("lib", "unusedUser"), unused)
        self.assertIn(("extra", "unusedHelper"), unused)

    def test_php_exports_and_import_symbols_are_additive(self) -> None:
        if shutil.which("php") is None:
            self.skipTest("php runtime is not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_dir = root / "src" / "domain" / "model"
            model_dir.mkdir(parents=True)
            model_dir.joinpath("user.php").write_text(
                "<?php\n"
                "namespace App\\Domain\\Model;\n"
                "class User {}\n"
                "class UnusedUser {}\n",
                encoding="utf-8",
            )
            controller_dir = root / "src" / "interfaces"
            controller_dir.mkdir(parents=True)
            controller_dir.joinpath("controller.php").write_text(
                "<?php\n"
                "namespace App\\Interfaces;\n"
                "use App\\Domain\\Model\\User;\n"
                "class Controller {}\n",
                encoding="utf-8",
            )

            result = extract_code("php", root, ())

        controller_import = result.extraction_result.files[
            "src/interfaces/controller"
        ].imports[0]
        self.assertEqual(controller_import.imported_name, "")
        self.assertEqual(
            [symbol.name for symbol in controller_import.imported_symbols],
            ["User"],
        )
        unused = {
            (source_export.source_id, source_export.name)
            for source_export in find_unused_exports(result.extraction_result)
        }
        self.assertNotIn(("src/domain/model/user", "User"), unused)
        self.assertIn(("src/domain/model/user", "UnusedUser"), unused)

    def assert_has_nested_source_files(self, result) -> None:
        depths = {
            len(Path(path).with_suffix("").parts)
            for path in result.extraction_result.files
            if path.startswith("src/")
        }
        self.assertGreaterEqual(max(depths), 4)

    def assert_has_classes_and_functions(self, result) -> None:
        classes = {
            class_definition.name
            for extracted_file in result.extraction_result.files.values()
            for class_definition in extracted_file.classes
        }
        functions = {
            function_definition.name
            for extracted_file in result.extraction_result.files.values()
            for function_definition in extracted_file.functions
        }
        self.assertGreaterEqual(len(classes), 2)
        self.assertGreaterEqual(len(functions), 1)

    def assert_has_metrics(self, result) -> None:
        for source_file in result.extraction_result.files.values():
            self.assertGreater(source_file.line_count, 0)
            self.assertGreater(source_file.code_line_count, 0)
            self.assertGreaterEqual(source_file.public_symbol_count, 0)

    def assert_scans_typescript_extensions(self, result) -> None:
        self.assertIn("src/domain/model/profile", result.extraction_result.files)
        self.assertIn("src/domain/services/audit", result.extraction_result.files)
        self.assertIn("src/interfaces/http/view", result.extraction_result.files)

    def assert_has_import_barrier_metadata(self, language: str, result) -> None:
        if language == "python":
            activate_imports = imports_by_target(
                result,
                "src/application/use_cases/activate",
            )
            self.assertTrue(activate_imports["src/domain/model/user"])
            self.assertTrue(activate_imports["src/domain/services/policy"])
            self.assertFalse(activate_imports["dataclasses"])
            self.assertEqual(
                import_crossing_types_by_target(
                    result,
                    "src/application/use_cases/activate",
                )["src/domain/model/user"],
                {"symbol"},
            )
            return

        if language == "typescript":
            controller_imports = imports_by_target(
                result,
                "src/interfaces/http/controller",
            )
            self.assertTrue(controller_imports["src/application/use_cases/activate"])
            self.assertTrue(controller_imports["src/domain/model/user"])
            self.assertFalse(controller_imports["node:path"])
            self.assertEqual(
                import_crossing_types_by_target(
                    result,
                    "src/interfaces/http/controller",
                )["src/application/use_cases/activate"],
                {"symbol"},
            )
            return

        if language == "php":
            controller_imports = imports_by_target(
                result,
                "src/interfaces/http/controller",
            )
            self.assertTrue(controller_imports["src/application/use_cases/activate"])
            self.assertTrue(controller_imports["src/domain/model/user"])
            self.assertFalse(controller_imports["DateTimeImmutable"])
            self.assertEqual(
                import_crossing_types_by_target(
                    result,
                    "src/interfaces/http/controller",
                )["src/domain/model/user"],
                {"symbol"},
            )
            return

        self.fail(f"Unexpected language: {language}")

    def assert_has_import_alias_metadata(self, language: str, result) -> None:
        controller_aliases = import_aliases_by_target(
            result,
            "src/interfaces/http/controller",
        )

        if language == "python":
            self.assertTrue(controller_aliases["json"])
            self.assertTrue(controller_aliases["src/domain/model/user"])
            self.assertFalse(controller_aliases["src/application/use_cases/activate"])
            return

        if language == "typescript":
            self.assertTrue(controller_aliases["node:path"])
            self.assertTrue(controller_aliases["src/domain/model/user"])
            self.assertFalse(controller_aliases["src/application/use_cases/activate"])
            return

        if language == "php":
            self.assertTrue(controller_aliases["DateTimeImmutable"])
            self.assertTrue(controller_aliases["src/domain/model/user"])
            self.assertFalse(controller_aliases["src/application/use_cases/activate"])
            return

        self.fail(f"Unexpected language: {language}")

    def assert_has_argument_count_metadata(self, language: str, result) -> None:
        if language == "python":
            self.assertEqual(
                method_counts(result, "src/domain/model/user", "User", "__init__"),
                (2, 1),
            )
            self.assertEqual(
                method_counts(result, "src/domain/model/user", "User", "activate"),
                (0, 0),
            )
            self.assertEqual(
                function_counts(
                    result,
                    "src/application/use_cases/activate",
                    "nullable_label",
                ),
                (1, 0),
            )
            return

        if language == "typescript":
            self.assertEqual(
                method_counts(result, "src/domain/model/user", "User", "constructor"),
                (2, 1),
            )
            self.assertEqual(
                method_counts(
                    result,
                    "src/interfaces/http/controller",
                    "ActivationController",
                    "constructor",
                ),
                (1, 0),
            )
            self.assertEqual(
                function_counts(
                    result,
                    "src/application/use_cases/activate",
                    "nullableLabel",
                ),
                (1, 0),
            )
            self.assertEqual(
                function_counts(
                    result,
                    "src/application/use_cases/activate",
                    "optionalLabel",
                ),
                (1, 1),
            )
            return

        if language == "php":
            self.assertEqual(
                method_counts(result, "src/domain/model/user", "User", "__construct"),
                (2, 1),
            )
            self.assertEqual(
                method_counts(result, "src/domain/model/user", "User", "__toString"),
                (0, 0),
            )
            self.assertEqual(
                function_counts(
                    result,
                    "src/application/use_cases/activate",
                    "nullableLabel",
                ),
                (1, 0),
            )
            return

        self.fail(f"Unexpected language: {language}")

    def assert_has_class_property_metadata(self, language: str, result) -> None:
        if language == "python":
            self.assertEqual(
                class_properties(result, "src/domain/model/user", "User"),
                {"user_id": False, "active": False, "nickname": True},
            )
            return

        if language == "typescript":
            self.assertEqual(
                class_properties(result, "src/domain/model/user", "User"),
                {"id": False, "active": False, "nickname": True},
            )
            return

        if language == "php":
            self.assertEqual(
                class_properties(result, "src/domain/model/user", "User"),
                {"nickname": True, "id": False, "active": False},
            )
            return

        self.fail(f"Unexpected language: {language}")

    def assert_has_visibility_metadata(self, language: str, result) -> None:
        self.assertEqual(
            class_visibility(result, "src/domain/model/user", "User"),
            ("public", "public"),
        )

        if language == "typescript":
            self.assertEqual(
                method_visibility(
                    result,
                    "src/domain/model/user",
                    "User",
                    "fingerprint",
                ),
                ("public", "public"),
            )
            return

        if language == "php":
            self.assertEqual(
                method_visibility(
                    result,
                    "src/domain/model/user",
                    "User",
                    "__toString",
                ),
                ("public", "public"),
            )
            return

        if language == "python":
            self.assertEqual(
                method_visibility(
                    result,
                    "src/domain/model/user",
                    "User",
                    "activate",
                ),
                ("public", "public"),
            )
            return

        self.fail(f"Unexpected language: {language}")


def app_fixtures() -> tuple[AppFixture, ...]:
    return (
        AppFixture(language="python", root=APPS_DIR / "python"),
        AppFixture(language="typescript", root=APPS_DIR / "typescript", runtime="node"),
        AppFixture(language="php", root=APPS_DIR / "php", runtime="php"),
    )


def extractor_batch_fixtures() -> tuple[ExtractorBatchFixture, ...]:
    return (
        ExtractorBatchFixture(
            language="python",
            extension=".py",
            content="def sample():\n    pass\n",
            batch_size_patch="modwire.extractors.python.PythonExtractor.batch_size",
        ),
        ExtractorBatchFixture(
            language="typescript",
            extension=".ts",
            content="export function sample(): void {}\n",
            batch_size_patch=(
                "modwire.extractors.typescript.TypeScriptExtractor.batch_size"
            ),
        ),
        ExtractorBatchFixture(
            language="php",
            extension=".php",
            content="<?php\nfunction sample(): void {}\n",
            batch_size_patch="modwire.extractors.php.PhpExtractor.batch_size",
        ),
    )


def internal_edges(result) -> set[tuple[str, str]]:
    source_files = set(result.extraction_result.files)
    return {
        (edge.from_id, edge.to_id)
        for edge in result.graph.edges
        if edge.from_id in source_files and edge.to_id in source_files
    }


def count_source_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.suffix in source_extensions())


def extractor_script(name: str) -> Path:
    return (
        Path(__file__).parent.parent
        / "src"
        / "modwire"
        / "extractors"
        / "scripts"
        / name
    )


def extractor_output(cmd: list[str], input_data: dict[str, str] | None = None) -> dict:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=json.dumps(input_data) if input_data is not None else None,
        check=True,
    )
    return json.loads(result.stdout)


def fake_batch_run(cmd, *, input=None, **kwargs):
    paths_by_source_id = json.loads(input or "{}")
    return SimpleNamespace(
        stdout=json.dumps(
            {source_id: source_file_payload() for source_id in paths_by_source_id}
        )
    )


def batch_input_sizes(run_mock) -> list[int]:
    return [len(json.loads(call.kwargs["input"])) for call in run_mock.call_args_list]


def source_file_payload() -> dict[str, object]:
    return {
        "imports": [],
        "exports": [],
        "classes": [],
        "interfaces": [],
        "types": [],
        "abstract_classes": [],
        "functions": [],
        "line_count": 1,
        "code_line_count": 1,
        "public_symbol_count": 0,
    }


def source_extensions() -> set[str]:
    return {".py", ".ts", ".tsx", ".js", ".jsx", ".php"}


def imports_by_target(result, source_id: str) -> dict[str, bool]:
    return {
        source_import.normalized_path: source_import.file_barrier_crossed
        for source_import in result.extraction_result.files[source_id].imports
    }


def import_crossing_types_by_target(result, source_id: str) -> dict[str, set[str]]:
    imports: dict[str, set[str]] = {}
    for source_import in result.extraction_result.files[source_id].imports:
        imports.setdefault(source_import.normalized_path, set()).add(
            source_import.crossing_type
        )
    return imports


def import_aliases_by_target(result, source_id: str) -> dict[str, bool]:
    return {
        source_import.normalized_path: source_import.is_aliased
        for source_import in result.extraction_result.files[source_id].imports
    }


def method_counts(
    result,
    source_id: str,
    class_name: str,
    method_name: str,
) -> tuple[int, int]:
    for class_definition in result.extraction_result.files[source_id].classes:
        if class_definition.name != class_name:
            continue
        for method in class_definition.methods:
            if method.name == method_name:
                return method.declared_args, method.optional_args
    raise AssertionError(f"Missing method {source_id}:{class_name}.{method_name}")


def function_counts(result, source_id: str, function_name: str) -> tuple[int, int]:
    for function in result.extraction_result.files[source_id].functions:
        if function.name == function_name:
            return function.declared_args, function.optional_args
    raise AssertionError(f"Missing function {source_id}:{function_name}")


def class_properties(result, source_id: str, class_name: str) -> dict[str, bool]:
    for class_definition in result.extraction_result.files[source_id].classes:
        if class_definition.name == class_name:
            return {
                property_definition.name: property_definition.is_optional
                for property_definition in class_definition.properties
            }
    raise AssertionError(f"Missing class {source_id}:{class_name}")


def class_visibility(result, source_id: str, class_name: str) -> tuple[str, str]:
    for class_definition in result.extraction_result.files[source_id].classes:
        if class_definition.name == class_name:
            return class_definition.visibility, class_definition.visibility_intent
    raise AssertionError(f"Missing class {source_id}:{class_name}")


def method_visibility(
    result,
    source_id: str,
    class_name: str,
    method_name: str,
) -> tuple[str, str]:
    for class_definition in result.extraction_result.files[source_id].classes:
        if class_definition.name != class_name:
            continue
        for method in class_definition.methods:
            if method.name == method_name:
                return method.visibility, method.visibility_intent
    raise AssertionError(f"Missing method {source_id}:{class_name}.{method_name}")


def function_visibility(
    result,
    source_id: str,
    function_name: str,
) -> tuple[str, str]:
    for function in result.extraction_result.files[source_id].functions:
        if function.name == function_name:
            return function.visibility, function.visibility_intent
    raise AssertionError(f"Missing function {source_id}:{function_name}")


if __name__ == "__main__":
    unittest.main()
