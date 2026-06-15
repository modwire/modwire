from __future__ import annotations

import unittest

from types import SimpleNamespace

from modwire.architecture import (
    AnalyzerInfo,
    ArchitectureCluster,
    ArchitectureBoundaryRule,
    ArchitectureConfig,
    ArchitectureConfigError,
    ArchitectureFlowRules,
    ArchitectureMap,
    ArchitecturePolicyEvaluator,
    ArchitectureRules,
    ArchitectureTagRule,
    CoherenceSummary,
    CrossModuleDependency,
    DependencyHotspot,
    EdgeRuleViolation,
    FlowViolation,
    TagMap,
    TagMatch,
    TagMatcher,
    analyzer_metadata,
    cluster_code,
    coherence_summary,
    find_hotspots,
    map_code,
    render_violations,
    structured_groups,
    supported_analyzers,
    validate_policy_config,
    violation_to_dict,
)
from modwire.extraction import CodeMap, ExtractionResult, ExtractionSummary
from modwire.graph import DependencyGraph


class ArchitectureApiTest(unittest.TestCase):
    def test_architecture_package_exports_policy_and_violation_types(self) -> None:
        self.assertIsNotNone(ArchitecturePolicyEvaluator)
        self.assertEqual(
            EdgeRuleViolation(
                source_id="src/app",
                target_id="src/domain",
                source_pattern="src/*",
                target_pattern="src/*",
                rule_name="feature-boundary",
            ).rule_name,
            "feature-boundary",
        )
        self.assertEqual(
            FlowViolation(
                violation_type="backward-flow",
                path=("src/ui", "src/domain"),
                violation_index=0,
                rule_name="analyzer:backward-flow",
                message="src/ui points backward to src/domain",
            ).message,
            "src/ui points backward to src/domain",
        )
        self.assertEqual(
            supported_analyzers(),
            ("backward-flow", "no-reentry", "no-cycles"),
        )
        self.assertTrue(all(isinstance(info, AnalyzerInfo) for info in analyzer_metadata()))

    def test_compiled_tag_matcher_maps_code_and_exposes_match_details(self) -> None:
        matcher = TagMatcher(
            SimpleNamespace(
                language="python",
                architecture_root="src",
                rules=SimpleNamespace(
                    tags=(
                        SimpleNamespace(
                            name="module",
                            match="features/*",
                            excluded_patterns=("features/*/generated/**",),
                        ),
                        SimpleNamespace(
                            name="layer",
                            match="features/*/domain",
                            excluded_patterns=(),
                        ),
                    )
                ),
            )
        )
        code_map = CodeMap(
            graph=DependencyGraph(),
            extraction_result=ExtractionResult(
                files={
                    "src/features/billing/domain": object(),
                    "src/features/billing/generated/client": object(),
                    "src/shared/logging": object(),
                },
                summary=ExtractionSummary(3, 3, 0),
            ),
            runtime_command="python",
        )

        module = matcher.match("src/features/billing/domain", "module")
        layer = matcher.first_match("src/features/billing/domain", ("layer", "module"))
        tag_map = matcher.map_code_map(code_map)

        self.assertIsInstance(module, TagMatch)
        self.assertEqual(module.name, "module")
        self.assertEqual(module.pattern, "features/*")
        self.assertEqual(module.captured_path, "src/features/billing")
        self.assertTrue(module.is_wildcard)
        self.assertEqual(layer.name, "layer")
        self.assertIsNone(matcher.match("src/features/billing/generated/client", "module"))
        self.assertEqual(matcher.display_path("src/features/billing/domain"), "features/billing/domain")
        self.assertIsInstance(tag_map, TagMap)
        self.assertEqual(
            [match.name for match in tag_map.tags_for("src/features/billing/domain")],
            ["module", "layer"],
        )
        self.assertEqual(
            tag_map.first_match("src/features/billing/domain", ("module",)).captured_path,
            "src/features/billing",
        )

    def test_architecture_config_models_validate_and_evaluate_policy(self) -> None:
        graph = DependencyGraph()
        graph.add_edge("src/features/billing/ui", "src/features/billing/domain")
        config = ArchitectureConfig(
            language="python",
            architecture_root="src",
            rules=ArchitectureRules(
                tags=(
                    ArchitectureTagRule(name="ui", match="features/*/ui"),
                    ArchitectureTagRule(name="domain", match="features/*/domain"),
                ),
                boundaries=(
                    ArchitectureBoundaryRule(
                        source="features/*/ui",
                        disallow=("features/*/domain",),
                    ),
                ),
                flow=ArchitectureFlowRules(),
            ),
        )

        violations = ArchitecturePolicyEvaluator().evaluate(graph, config)

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].source_pattern, "features/*/ui")
        self.assertEqual(
            violation_to_dict(violations[0]),
            {
                "violation_type": "edge-rule",
                "source_id": "src/features/billing/ui",
                "target_id": "src/features/billing/domain",
                "source_pattern": "features/*/ui",
                "target_pattern": "features/*/domain",
                "rule_name": "boundary:features/*/ui->features/*/domain:deny",
            },
        )

    def test_architecture_config_errors_are_structured(self) -> None:
        with self.assertRaises(ArchitectureConfigError) as context:
            validate_policy_config(
                {
                    "language": "python",
                    "rules": {
                        "flow": {
                            "analyzers": ("missing-analyzer",),
                        }
                    },
                }
            )

        payload = context.exception.to_dict()
        self.assertEqual(payload["error"], "invalid_architecture_config")
        self.assertIn("rules.flow.analyzers", payload["issues"][0]["field"])
        self.assertIn("Unsupported flow analyzer", payload["issues"][0]["message"])

    def test_flow_violations_have_stable_dict_shape(self) -> None:
        violation = FlowViolation(
            violation_type="backward-flow",
            path=("src/ui", "src/domain"),
            violation_index=1,
            rule_name="analyzer:backward-flow",
            message="layer order violated",
        )

        self.assertEqual(
            violation.to_dict(),
            {
                "violation_type": "backward-flow",
                "path": ("src/ui", "src/domain"),
                "violation_index": 1,
                "rule_name": "analyzer:backward-flow",
                "message": "layer order violated",
            },
        )

    def test_architecture_insights_summarize_maps_clusters_and_hotspots(self) -> None:
        graph = DependencyGraph()
        graph.add_edge("src/features/billing/ui", "src/features/billing/domain")
        graph.add_edge("src/features/orders/ui", "src/features/billing/domain")
        graph.add_edge("src/features/orders/ui", "json")
        code_map = CodeMap(
            graph=graph,
            extraction_result=ExtractionResult(
                files={
                    "src/features/billing/ui": object(),
                    "src/features/billing/domain": object(),
                    "src/features/orders/ui": object(),
                },
                summary=ExtractionSummary(3, 3, 0),
            ),
            runtime_command="python",
        )
        config = ArchitectureConfig(
            language="python",
            architecture_root="src",
            rules=ArchitectureRules(
                tags=(
                    ArchitectureTagRule(name="module", match="features/*"),
                    ArchitectureTagRule(name="layer", match="features/*/ui"),
                    ArchitectureTagRule(name="layer", match="features/*/domain"),
                ),
            ),
        )

        mapped = map_code(code_map, config)
        clusters = cluster_code(code_map, group_depth=3)
        hotspots = find_hotspots(code_map)
        coherence = coherence_summary(code_map)

        self.assertIsInstance(mapped, ArchitectureMap)
        self.assertEqual(
            mapped.modules["src/features/billing"],
            ("src/features/billing/domain", "src/features/billing/ui"),
        )
        self.assertEqual(mapped.unknown_files, ())
        self.assertEqual(
            mapped.cross_module_dependencies,
            (
                CrossModuleDependency(
                    "src/features/orders",
                    "src/features/billing",
                    1,
                ),
            ),
        )
        self.assertTrue(all(isinstance(cluster, ArchitectureCluster) for cluster in clusters))
        self.assertEqual(clusters[0].name, "src/features/billing")
        self.assertTrue(all(isinstance(hotspot, DependencyHotspot) for hotspot in hotspots))
        self.assertEqual(hotspots[0].source_id, "src/features/billing/domain")
        self.assertIsInstance(coherence, CoherenceSummary)
        self.assertEqual(
            coherence.roots,
            ("src/features/billing/ui", "src/features/orders/ui"),
        )
        self.assertEqual(coherence.leaves, ("src/features/billing/domain",))
        self.assertEqual(coherence.external_dependencies, ("json",))

    def test_rendering_hooks_support_structured_groups_and_path_display(self) -> None:
        violation = EdgeRuleViolation(
            source_id="src/app/ui",
            target_id="src/app/domain",
            source_pattern="ui",
            target_pattern="domain",
            rule_name="boundary:ui->domain:deny",
        )

        rendered = render_violations(
            (violation,),
            path_display=lambda path: path.removeprefix("src/"),
        )
        groups = structured_groups((violation,))

        self.assertIn("app/ui -> [app/domain]", rendered)
        self.assertEqual(groups[0]["title"], "Edge Rule Violations")
        self.assertEqual(groups[0]["violations"][0]["type"], "edge-rule")


if __name__ == "__main__":
    unittest.main()
