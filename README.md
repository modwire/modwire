# modwire

`modwire` turns code maps from
[`modwire-extraction`](https://github.com/9orky/modwire-extraction) into
architecture reports: boundary maps, dependency-flow violations, shape-policy
violations, and architecture insights.

## Installation

```bash
python -m pip install modwire
```

## Quick Start

```python
from pathlib import Path

from modwire.architecture import (
    ArchitectureConfig,
    ArchitectureReportRunner,
    BoundariesConfig,
    FlowRealm,
    FlowRules,
    ShapeConfig,
    TagRule,
)
from modwire_extraction import ModwireExtraction

code_map = ModwireExtraction(Path("src")).generate_map("python")

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
            realms=(
                FlowRealm(
                    name="feature",
                    layers=("domain", "ui"),
                ),
            ),
        ),
    ),
    shape=ShapeConfig(
        max_functions_per_file=8,
        max_methods_per_class=12,
        allow_import_aliases=False,
    ),
)

report = ArchitectureReportRunner(config).run(code_map)

print(report.map.modules)
print(report.violations.flow.violations)
print(report.violations.shape.violations)
print(report.insights.hotspots[:5])
```

## Report Sections

`ArchitectureReportRunner` returns a typed `ArchitectureReport` with three
top-level sections:

- `map`: normalized module and layer groupings plus unknown files
- `violations`: dependency-flow and shape-policy violations
- `insights`: clusters, hotspots, dependency coherence, callable graph, and
  unused exports

Reports are Pydantic models, so they can be serialized with `model_dump()` or
`model_dump_json()`.

```python
payload = report.model_dump(mode="json")
```

## Configuration

Boundary tags classify source IDs. Flow rules then use those tags to detect
backward dependencies, module cycles, and module re-entry.

```python
from modwire.architecture import BoundariesConfig, FlowRules, TagRule

boundaries = BoundariesConfig(
    tags=(
        TagRule(name="module", match="features/*"),
        TagRule(name="api", match="features/*/api"),
        TagRule(name="domain", match="features/*/domain"),
    ),
    flow=FlowRules(
        module_tag="module",
        layers=("domain", "api"),
    ),
)
```

Shape limits are disabled with `-1` and enabled with non-negative integers.

```python
from modwire.architecture import ShapeConfig

shape = ShapeConfig(
    max_classes_per_file=3,
    max_function_lines=40,
    require_joined_imports=True,
)
```

## Migration

The current API is intentionally OOP-first. Older helper functions such as
`evaluate_shape`, `render_callable_report`, `structured_callable_report`,
`find_unused_exports`, `map_code`, `find_hotspots`, and
`coherence_summary` have been replaced by `ArchitectureReportRunner`.

See [CHANGELOG.md](CHANGELOG.md) before publishing or upgrading across the next
major release.

## Development

See [Development checks](docs/wiki/Development-checks.md) for the local command
set used before pull requests and releases.

## Contributing

Feature requests and bug reports are tracked through GitHub Issues:

- Open a feature request for architecture analyzers, output formats, or
  integrations.
- Open a bug report for incorrect architecture violations, graph output, shape
  reports, callable reports, unused export reports, packaging problems, or
  documentation mismatches.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the information to include and the
checks to run before opening a pull request.
