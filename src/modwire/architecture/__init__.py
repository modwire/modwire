from .analyzers import AnalyzerInfo, analyzer_metadata, supported_analyzers
from .config import (
    ArchitectureBoundaryRule,
    ArchitectureConfig,
    ArchitectureConfigError,
    ArchitectureConfigIssue,
    ArchitectureFlowRules,
    ArchitectureRules,
    ArchitectureTagRule,
    validate_edge_rules,
    validate_flow_rules,
    validate_policy_config,
    validate_tags,
)
from .insights import (
    ArchitectureCluster,
    ArchitectureMap,
    CoherenceSummary,
    CrossModuleDependency,
    DependencyHotspot,
    cluster_code,
    coherence_summary,
    find_hotspots,
    map_code,
)
from .matching import TagMap, TagMatch, TagMatcher
from .policy import ArchitecturePolicyEvaluator
from .render import render_violations, structured_groups
from .violations import EdgeRuleViolation, FlowViolation, violation_to_dict

__all__ = [
    "AnalyzerInfo",
    "ArchitectureCluster",
    "ArchitectureBoundaryRule",
    "ArchitectureConfig",
    "ArchitectureConfigError",
    "ArchitectureConfigIssue",
    "ArchitectureFlowRules",
    "ArchitectureMap",
    "ArchitecturePolicyEvaluator",
    "ArchitectureRules",
    "ArchitectureTagRule",
    "CoherenceSummary",
    "CrossModuleDependency",
    "DependencyHotspot",
    "EdgeRuleViolation",
    "FlowViolation",
    "TagMap",
    "TagMatch",
    "TagMatcher",
    "analyzer_metadata",
    "cluster_code",
    "coherence_summary",
    "find_hotspots",
    "map_code",
    "render_violations",
    "structured_groups",
    "supported_analyzers",
    "validate_edge_rules",
    "validate_flow_rules",
    "validate_policy_config",
    "validate_tags",
    "violation_to_dict",
]
