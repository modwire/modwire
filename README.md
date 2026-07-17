# Modwire Architecture

Modwire Architecture is the typed architecture library for the Modwire ecosystem.
It analyzes already extracted code maps and reports boundaries, shape violations,
and insights without filesystem, persistence, transport, or rendering work.

```python
from modwire_architecture import ArchitectureConfig, Modwire
from modwire_extraction import QueryableCodeMap


def analyze(code_map: QueryableCodeMap):
    return Modwire().architecture(ArchitectureConfig()).analyze(code_map)
```

Install the library with:

```bash
python -m pip install 'modwire-architecture>=6,<7'
```

`analyze()` returns a versioned `ArchitectureAnalysis` with explicit `pass`,
`violation`, `not-applicable`, and `unsupported` outcomes plus deterministic
insights. See the [analysis contract](docs/architecture-analysis-contract.md).

## Package shape

- `modwire_architecture.architecture` — the supported analysis API, policies,
  typed outcomes, evidence, and insights.
- `modwire_architecture.shared.config` — immutable, validated analysis profiles.
- `modwire_architecture.shared.report` — legacy report metadata used internally
  during the transition to the public analysis contract.

Package-identity guidance is available in
[Migrating from Modwire to Modwire Architecture](docs/migration-6.md).
The historical [Modwire 4 to 5 migration](docs/migration-5.md) remains available
for existing `modwire` consumers.

## Model contracts

Public value objects derive from one of three Pydantic bases:
`ModwireModel`, `ModwireConfigModel`, or `ModwireReportModel`. They are frozen,
reject unknown fields, validate defaults, normalize surrounding string
values through domain validators, and provide dictionary, JSON, and YAML
round-trip helpers without filesystem orchestration.

## Development

```bash
uv sync --all-groups
uv run pytest
uv run ruff check src tests
uv build
```
