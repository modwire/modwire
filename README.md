# Modwire

Modwire is the typed coordination library for the Modwire ecosystem. It composes
in-memory architecture analysis, Siren documents, and Mermaid diagrams without
embedding filesystem or command-line orchestration in the library.

```python
from modwire import ArchitectureConfig, Modwire
from modwire_extraction import QueryableCodeMap


def analyze(code_map: QueryableCodeMap):
    return Modwire().architecture(ArchitectureConfig()).report(code_map)
```

Core accepts in-memory configuration and an already extracted code map. Install
`modwire-cli` when paths, configuration directories, or generated files are
involved.

Install `modwire-cli` when you need the command line:

```bash
pip install modwire-cli
modwire --config-dir .modwire architecture health src python
```

## Package shape

- `modwire.architecture` — architecture maps, boundary policies, shape checks,
  insights, and typed reports.
- `modwire.code` — validated in-memory code-package values.
- `modwire.layers` — named layer contracts; orchestration remains to be defined.
- `modwire.modules` — named module contracts; orchestration remains to be defined.
- `modwire.projects` — project coordination contracts for modules and layers;
  orchestration remains to be defined.
- `modwire.shared.config` — immutable, validated configuration contracts.
- `modwire.shared.report` — architecture report contracts and metadata.

Scaffolding and glossary functionality are not part of this package. The
work-in-progress [modwire-mcp](https://github.com/modwire/modwire-mcp) project
retains the ecosystem's crucial scaffolding surface.

The repeatable GitHub coordination model is frozen in the
[ecosystem playbook](docs/governance/github-ecosystem.md) and its
[executable source-of-truth contract](.github/modwire-ecosystem.yml). The
contract's package registry derives repository membership and the shared
Project component taxonomy; CI validates it with strict Pydantic models. The
[Python workflow contract](docs/governance/python-workflows.md) provides the
standard reusable CI and release procedures for member packages.

## Ecosystem

Modwire coordinates three independently released building blocks:

- [modwire-extraction](https://github.com/modwire/modwire-extraction) — canonical
  code extraction. Follow its [Trustworthy Foundation](https://github.com/modwire/modwire-extraction/milestone/2),
  [Canonical Symbol Model v2](https://github.com/modwire/modwire-extraction/milestone/1),
  and [Extensible Production Platform](https://github.com/modwire/modwire-extraction/milestone/3)
  milestones.
- [modwire-siren](https://github.com/modwire/modwire-siren) — typed Siren and
  OpenAPI integration. See [Siren integration improvements](https://github.com/modwire/modwire-siren/milestone/1).
- [modwire-mermaid](https://github.com/modwire/modwire-mermaid) — typed,
  deterministic Mermaid source. See [Package improvements](https://github.com/modwire/modwire-mermaid/milestone/1).

The architecture work here tracks [Architecture Policy Core](https://github.com/modwire/modwire/milestone/1)
and [Architecture Insights and Integration Ergonomics](https://github.com/modwire/modwire/milestone/2).
Modwire 5 migration guidance is available in
[Migrating from Modwire 4 to 5](docs/migration-5.md).

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
