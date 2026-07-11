# Modwire

Modwire is the typed coordination library for the Modwire ecosystem. It composes
code extraction, architecture analysis, Siren documents, and Mermaid diagrams
without embedding a command-line runtime in the library.

```python
from modwire import Modwire

modwire = Modwire()
code_map = modwire.extract("src", "python")
architecture = modwire.architecture()
```

Install `modwire-cli` when you need the command line:

```bash
pip install modwire-cli
modwire --config-dir .modwire architecture health src python
```

## Package shape

- `modwire.architecture` — architecture maps, boundary policies, shape checks,
  insights, and typed reports.
- `modwire.code` — common code-package and extraction access shared across the
  ecosystem.
- `modwire.layers` — named layer contracts; orchestration remains to be defined.
- `modwire.modules` — named module contracts; orchestration remains to be defined.
- `modwire.projects` — project coordination contracts for modules and layers;
  orchestration remains to be defined.
- `modwire.shared.config` — immutable, validated configuration contracts.
- `modwire.shared.report` — architecture report contracts and metadata.

Scaffolding and glossary functionality are not part of this package. The
work-in-progress [modwire-mcp](https://github.com/9orky/modwire-mcp) project
retains the ecosystem's crucial scaffolding surface.

## Ecosystem

Modwire coordinates three independently released building blocks:

- [modwire-extraction](https://github.com/9orky/modwire-extraction) — canonical
  code extraction. Follow its [Trustworthy Foundation](https://github.com/9orky/modwire-extraction/milestone/2),
  [Canonical Symbol Model v2](https://github.com/9orky/modwire-extraction/milestone/1),
  and [Extensible Production Platform](https://github.com/9orky/modwire-extraction/milestone/3)
  milestones.
- [modwire-siren](https://github.com/9orky/modwire-siren) — typed Siren and
  OpenAPI integration. See [Siren integration improvements](https://github.com/9orky/modwire-siren/milestone/1).
- [modwire-mermaid](https://github.com/9orky/modwire-mermaid) — typed,
  deterministic Mermaid source. See [Package improvements](https://github.com/9orky/modwire-mermaid/milestone/1).

The architecture work here tracks [Architecture Policy Core](https://github.com/9orky/modwire/milestone/1)
and [Architecture Insights and Integration Ergonomics](https://github.com/9orky/modwire/milestone/2).
Current integration follow-ups include [multiple flow realms](https://github.com/9orky/modwire/issues/13)
and [explicit duplicate tag behavior](https://github.com/9orky/modwire/issues/14).

## Model contracts

Public value objects derive from one of three Pydantic bases:
`ModwireModel`, `ModwireConfigModel`, or `ModwireReportModel`. They are frozen,
reject unknown fields, validate defaults, normalize surrounding string
values through domain validators, and provide dictionary, JSON, YAML, and file
round-trip helpers.

## Development

```bash
uv sync --all-groups
uv run pytest
uv run ruff check src tests
uv build
```
