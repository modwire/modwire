from __future__ import annotations

import unittest

from types import SimpleNamespace

from modwire.architecture import (
    ArchitecturePolicyEvaluator,
    EdgeRuleViolation,
    FlowViolation,
    TagMap,
    TagMatch,
    TagMatcher,
    supported_analyzers,
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


if __name__ == "__main__":
    unittest.main()
