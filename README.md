# modwire

`modwire` maps architecture boundaries, evaluates violations, and renders
reports over code maps produced by
[`modwire-extraction`](https://github.com/9orky/modwire-extraction).

## Installation

```bash
python -m pip install modwire
```

## Quick Start

```python
from pathlib import Path

from modwire_extraction import ModwireExtraction
from modwire.architecture import (
    ArchitectureBoundaryRule,
    ArchitectureConfig,
    ArchitecturePolicyEvaluator,
    ArchitectureRules,
    ArchitectureTagRule,
    render_violations,
)

code_map = ModwireExtraction(Path("src")).generate_map("python")
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
    ),
)

violations = ArchitecturePolicyEvaluator().evaluate(
    code_map.dependency_graph,
    config,
)
print(render_violations(tuple(violations)))
```

## Architecture Mapping

```python
from modwire.architecture import coherence_summary, find_hotspots, map_code

architecture_map = map_code(code_map, config)
hotspots = find_hotspots(code_map, limit=5)
coherence = coherence_summary(code_map)

print(architecture_map.unknown_files)
print(hotspots)
print(coherence.external_dependencies)
```

## Shape Policy

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

## Reports

```python
from modwire import (
    find_unused_exports,
    render_callable_report,
    structured_callable_report,
)

print(render_callable_report(code_map))
print(structured_callable_report(code_map))

unused = find_unused_exports(code_map.extraction)
print([(export.source_id, export.name) for export in unused])
```

## Development

See [Development checks](docs/wiki/Development-checks.md) for the local command
set used before pull requests and releases.

## Contributing

Feature requests and bug reports are tracked through GitHub Issues:

- Open a feature request for architecture analyzers, report formats, or
  integrations.
- Open a bug report for incorrect architecture violations, graph reports, shape
  reports, callable reports, unused export reports, packaging problems, or
  documentation mismatches.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the information to include and the
checks to run before opening a pull request.
