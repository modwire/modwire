# Modwire Architecture

Modwire Architecture is the typed architecture library for the Modwire ecosystem. It composes
in-memory architecture analysis, Siren documents, and Mermaid diagrams without
embedding filesystem or command-line orchestration in the library.

```python
from modwire_architecture import ArchitectureConfig, Modwire
from modwire_extraction import QueryableCodeMap


def analyze(code_map: QueryableCodeMap):
    return Modwire().architecture(ArchitectureConfig()).report(code_map)
```

Install the library with:

```bash
python -m pip install 'modwire-architecture>=6,<7'
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

- `modwire_architecture.architecture` — architecture maps, boundary policies, shape checks,
  insights, and typed reports.
- `modwire_architecture.code` — validated in-memory code-package values.
- `modwire_architecture.layers` — named layer contracts; orchestration remains to be defined.
- `modwire_architecture.modules` — named module contracts; orchestration remains to be defined.
- `modwire_architecture.projects` — project coordination contracts for modules and layers;
  orchestration remains to be defined.
- `modwire_architecture.shared.config` — immutable, validated configuration contracts.
- `modwire_architecture.shared.report` — architecture report contracts and metadata.

Scaffolding and glossary functionality are not part of this package. The
current [modwire-mcp](https://github.com/modwire/modwire-mcp) repository is a
work-in-progress local scaffolding devserver, not yet an operational ecosystem
package. The MCP package becomes workable after `modwire-cli` exposes the
filesystem, project, and execution capabilities that MCP will coordinate.

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

The architecture work here tracks the
[Standalone Architecture Package](https://github.com/modwire/modwire-architecture/milestone/7)
milestone.
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
