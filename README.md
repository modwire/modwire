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

from modwire import extract_code

result = extract_code(
    "python",
    Path("src"),
    exclusions=("**/__pycache__/**",),
)

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

## Architecture Policy API

`modwire.architecture` exposes policy evaluation helpers for checking import
boundaries and common dependency-flow rules.

```python
from modwire.architecture import ArchitecturePolicyEvaluator, supported_analyzers

print(supported_analyzers())
# ("backward-flow", "no-reentry", "no-cycles")

evaluator = ArchitecturePolicyEvaluator()
```

## Development

```bash
uv run ruff check
uv run pytest
uv run python -m build --outdir dist
uv run twine check dist/*
```

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
