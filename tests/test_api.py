from __future__ import annotations

import unittest

import modwire
from modwire import (
    ArchitectureBoundaryRule,
    ArchitectureConfig,
    ArchitecturePolicyEvaluator,
    ArchitectureRules,
    CallableReportEntry,
    ShapeConfig,
    ShapePolicyEvaluator,
    build_dependency_graph,
    callable_report_entries,
    evaluate_shape,
    find_unused_exports,
    render_callable_report,
    structured_callable_report,
)
from modwire.definitions import SourceExport
from modwire.testing import (
    code_map,
    source_callable,
    source_call,
    source_class,
    source_file,
    source_function,
    source_import,
    source_method,
    source_property,
)


class PublicApiTest(unittest.TestCase):
    def test_modwire_exports_architecture_and_report_api_without_extraction_runtime(self) -> None:
        self.assertIsNotNone(ArchitecturePolicyEvaluator)
        self.assertIsNotNone(ShapePolicyEvaluator)
        self.assertIsNotNone(find_unused_exports)
        self.assertIsNotNone(callable_report_entries)
        self.assertFalse(hasattr(modwire, "extract_code"))
        self.assertFalse(hasattr(modwire, "discover_sources"))

    def test_graph_builder_reuses_extraction_graph_contract(self) -> None:
        graph = build_dependency_graph(
            {
                "app": source_file(imports=(source_import("dep"),)),
                "dep": source_file(),
            }
        )

        self.assertEqual(graph.node_ids(), ("app", "dep"))
        self.assertEqual(
            [(edge.from_id, edge.to_id) for edge in graph.edges],
            [("app", "dep")],
        )


class ArchitectureAndReportTest(unittest.TestCase):
    def test_architecture_policy_evaluates_dependency_graphs(self) -> None:
        sample = code_map(
            files=("src/features/billing/ui", "src/features/billing/domain"),
            edges=(("src/features/billing/ui", "src/features/billing/domain"),),
        )
        config = ArchitectureConfig(
            language="python",
            architecture_root="src",
            rules=ArchitectureRules(
                boundaries=(
                    ArchitectureBoundaryRule(
                        source="features/*/ui",
                        disallow=("features/*/domain",),
                    ),
                ),
            ),
        )

        violations = ArchitecturePolicyEvaluator().evaluate(
            sample.dependency_graph,
            config,
        )

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].source_id, "src/features/billing/ui")

    def test_shape_policy_reports_file_symbol_and_import_violations(self) -> None:
        sample = code_map(files=("app",))
        sample.extraction.files["app"] = source_file(
            imports=(source_import("shared", is_aliased=True),),
            classes=(
                source_class(
                    "Service",
                    methods=(source_method("run", line_count=12),),
                    properties=(source_property("maybe", is_optional=True),),
                    line_count=25,
                ),
            ),
            functions=(source_function("build", line_count=8),),
            line_count=30,
            code_line_count=20,
            public_symbol_count=2,
        )

        violations = evaluate_shape(
            sample,
            ShapeConfig(
                max_classes_per_file=0,
                max_functions_per_file=0,
                max_methods_per_class=0,
                max_function_lines=5,
                max_method_lines=5,
                max_class_lines=10,
                allow_optional_class_properties=False,
                allow_import_aliases=False,
            ),
        )

        self.assertGreaterEqual(len(violations), 6)
        self.assertEqual(
            ShapePolicyEvaluator()
            .evaluate(sample, ShapeConfig(max_classes_per_file=0))[0]
            .rule_name,
            "max_classes_per_file",
        )

    def test_callable_report_uses_extracted_callable_metadata(self) -> None:
        sample = code_map(files=("app",))
        sample.extraction.files["app"] = source_file(
            callables=(
                source_callable("app.run", name="run"),
                source_callable("app.save", name="save", line_start=4, line_end=6),
            ),
            calls=(
                source_call(
                    "app.run",
                    target_callable_id="app.save",
                    target_name="save",
                    expression="save()",
                    resolution="resolved",
                ),
            ),
        )

        entries = callable_report_entries(sample)
        report = render_callable_report(sample)

        self.assertTrue(all(isinstance(entry, CallableReportEntry) for entry in entries))
        self.assertEqual(len(structured_callable_report(sample)), 2)
        self.assertIn("save()", report)

    def test_unused_export_report_accepts_extraction_results_and_file_maps(self) -> None:
        exported = source_file()
        exported.exports.append(
            SourceExport(
                name="Unused",
                local_name="Unused",
                kind="class",
                crossing_type="symbol",
                path="",
                is_relative=False,
                normalized_path="",
                is_reexport=False,
                is_default=False,
                is_aliased=False,
                statement_id=1,
            )
        )
        sample = code_map(files=("api",))
        sample.extraction.files["api"] = exported

        from_extraction = find_unused_exports(sample.extraction)
        from_mapping = find_unused_exports(sample.extraction.files)

        self.assertEqual(from_extraction, from_mapping)
        self.assertEqual(from_extraction[0].name, "Unused")


if __name__ == "__main__":
    unittest.main()
