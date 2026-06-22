# modwire

`modwire` extracts source-code structure and import dependencies from Python,
TypeScript/JavaScript, and PHP projects. It returns typed Python objects that
you can use to build dependency graphs, inspect symbols, and evaluate
architecture rules.

## Installation

```bash
python -m pip install modwire
```

The Python extractor works with Python alone. TypeScript/JavaScript extraction
requires Node.js at runtime, and PHP extraction requires PHP at runtime.

## Quick Start

```python
from pathlib import Path

from modwire import discover_sources, extract_code

manifest = discover_sources(
    "python",
    Path("src"),
    exclusions=("**/__pycache__/**",),
)
result = extract_code("python", Path("src"), exclusions=manifest.exclusions)

print(result.extraction_result.summary.files_checked)
print(result.graph.node_ids())
print([(edge.from_id, edge.to_id) for edge in result.graph.edges])
```

Graph nodes use canonical extensionless source IDs, so equivalent Python,
TypeScript, and PHP projects can be compared through the same graph shape.

## Supported Languages


```python
from modwire import supported_languages

print(supported_languages())
# ("python", "typescript", "php")
```

Language-specific source IDs can be normalized without running a full
extraction:

```python
from modwire import normalize_source_id

print(normalize_source_id("typescript", "src/view.tsx"))
# "src/view"
```

## Extraction Options

Use `SourceRoots` when source IDs should be relative to a workspace root or to a
logical package prefix:

```python
from pathlib import Path

from modwire import SourceRoots, extract_code

code_map = extract_code(
    "python",
    Path("packages/billing/src"),
    source_roots=SourceRoots(
        workspace_root=Path("."),
        source_id_mode="relative_to_workspace_root",
    ),
)
```

Use `ExtractionCache` to reuse extraction output when files and extractor
implementations have not changed:

```python
from pathlib import Path

from modwire import ExtractionCache, extract_code

code_map = extract_code(
    "python",
    Path("src"),
    cache=ExtractionCache(Path(".modwire-cache")),
)

print(code_map.cache_status)
```

## Architecture Policy API

`modwire.architecture` exposes policy evaluation helpers for checking import
boundaries and common dependency-flow rules.

```python
from modwire import extract_code
from modwire.architecture import (
    ArchitectureBoundaryRule,
    ArchitectureConfig,
    ArchitectureFlowRealm,
    ArchitectureFlowRules,
    ArchitecturePolicyEvaluator,
    ArchitectureRules,
    ArchitectureTagRule,
    render_violations,
    supported_analyzers,
)

print(supported_analyzers())
# ("backward-flow", "no-reentry", "no-cycles")

code_map = extract_code("python", "src")
config = ArchitectureConfig(
    language="python",
    architecture_root="src",
    rules=ArchitectureRules(
        tags=(
            ArchitectureTagRule(name="module", match="features/*"),
            ArchitectureTagRule(name="ui", match="features/*/ui"),
            ArchitectureTagRule(name="domain", match="features/*/domain"),
        ),
        boundaries=(
            ArchitectureBoundaryRule(
                source="features/*/ui",
                disallow=("features/*/domain",),
                allow_same_match=True,
            ),
        ),
        flow=ArchitectureFlowRules(
            layers=("domain", "ui"),
            module_tag="module",
            analyzers=("no-cycles",),
        ),
    ),
)

violations = ArchitecturePolicyEvaluator().evaluate(code_map.graph, config)
print(render_violations(tuple(violations)))
```

For repositories with more than one module ladder, configure flow realms and run
the same analyzers across each module tag:

```python
config = ArchitectureConfig(
    language="python",
    architecture_root="src",
    rules=ArchitectureRules(
        tags=(
            ArchitectureTagRule(name="backend_module", match="features/*"),
            ArchitectureTagRule(name="gui_page", match="app/pages/*"),
            ArchitectureTagRule(name="domain", match="features/*/domain"),
            ArchitectureTagRule(name="application", match="features/*/application"),
        ),
        flow=ArchitectureFlowRules(
            realms=(
                ArchitectureFlowRealm(
                    name="backend",
                    module_tag="backend_module",
                    layers=("domain", "application"),
                ),
                ArchitectureFlowRealm(
                    name="gui",
                    module_tag="gui_page",
                ),
            ),
            analyzers=("backward-flow", "no-cycles"),
        ),
    ),
)
```

`backward-flow` evaluates realms with layers and skips layerless realms; scoped
analyzers such as `no-cycles` evaluate every configured realm.

Architecture insight helpers summarize ownership and graph pressure:

```python
from modwire.architecture import coherence_summary, find_hotspots, map_code

architecture_map = map_code(code_map, config)
hotspots = find_hotspots(code_map, limit=5)
coherence = coherence_summary(code_map)

print(architecture_map.cross_module_dependencies)
print(hotspots)
print(coherence.external_dependencies)
```

## Shape Policy API

Shape policies evaluate file, symbol, callable, property, and import metadata:

```python
from modwire import ShapePolicyEvaluator, evaluate_shape

violations = evaluate_shape(
    code_map,
    {
        "max_functions_per_file": 5,
        "max_methods_per_class": 10,
        "allow_import_aliases": False,
        "require_joined_imports": True,
    },
)

same_result = ShapePolicyEvaluator().evaluate(code_map, {})
print([violation.to_dict() for violation in violations])
print(same_result)
```

## Serialization And Exports

`CodeMap` results can be serialized for later analysis, and export metadata can
be used to find currently unused public symbols:

```python
from modwire import (
    deserialize_code_map,
    find_unused_exports,
    serialize_code_map,
)

payload = serialize_code_map(code_map)
loaded = deserialize_code_map(payload)

unused = find_unused_exports(loaded.extraction_result)
print([(export.source_id, export.name) for export in unused])
```

## Development

See [Development checks](docs/wiki/Development-checks.md) for the local command
set used before pull requests and releases.

## Contributing

Feature requests and bug reports are tracked through GitHub Issues:

- Open a feature request for new language support, graph metadata, architecture
  rules, export formats, or documentation examples.
- Open a bug report for incorrect extraction results, graph edges, architecture
  violations, packaging problems, or runtime failures.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the information to include and the
checks to run before opening a pull request.

Starter wiki pages are tracked under [docs/wiki](docs/wiki) so the GitHub Wiki
can be initialized with the same guidance.
