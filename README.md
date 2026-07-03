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

## Module Generation

`modwire.modules` can generate a module from any Copier template. A caller only
needs to create a normal Copier template directory and pass it to
`generate_module`.

```python
from pathlib import Path

from modwire.modules import generate_module

generate_module(
    "billing",
    Path("src/features"),
    Path("templates/modwire-module"),
    data={"service_name": "BillingService"},
)
```

If no template path is provided, `generate_module` uses the bundled `layered`
scaffolding. Pass `scaffolding="hexagonal"` for a pluggable domain/ports/adapters
structure, `scaffolding="clean"` for a domain/application/infrastructure/interface
module, `scaffolding="ddd_context"` for a bounded-context module, or
`scaffolding="crud_service"` for a CRUD-first service slice generated for
Python, TypeScript, and PHP. The CRUD scaffold uses Copier YAML includes to keep
shared questions separate from CRUD-specific questions. Bundled scaffoldings are
packaged with the distribution wheel.

## Project Generation

`modwire.projects` can generate a project authority and starter layout. The
default bundled project profile is `python-fastapi-ddd-uv`: Python, uv,
FastAPI, and a DDD-oriented package layout that mounts reusable `ddd_context`
module scaffolding under the application package.

```python
from pathlib import Path

from modwire.projects import generate_project

generate_project("acme", Path("services/acme"))
```

The generated project includes `.modwire/project.json`, which records the
resolved profile, layout, dependencies, module scaffolding, and operation names
for later project-aware automation.

Open an existing generated project with `open_project` to run project-aware
module operations against the recorded authority:

```python
from pathlib import Path

from modwire.projects import open_project

project = open_project(Path("services/acme"))

project.add_context("commerce")
project.add_module("billing", context_name="commerce")
project.remove_module("billing", context_name="commerce", dry_run=True)
```

The currently exposed project helpers cover reading the project authority,
adding contexts, adding modules, removing modules, and removing contexts. Module
generation uses the project's configured `module_scaffolding` and language output
root, so Python, TypeScript, and PHP profiles place generated files under their
own layout conventions.

Bundled project profiles currently include:

- `python-fastapi-ddd-uv`
- `typescript-nestjs-ddd-pnpm`
- `php-symfony-ddd-composer`

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

To prove the CRUD services work as separate REST services with JWT auth, run:

```bash
make prove-crud-rest-flow
```

The proof generates independent `orders` Python, `warehouse` TypeScript, and
`shipping` PHP services, starts each one as its own HTTP process, starts a
separate `auth` HTTP process, and sends data from orders to warehouse to
shipping over REST only. The command prints prefixed logs from every process and
finishes with a `DELIVERED` response from shipping.

The forge scaffold-family metadata models a noisier topology on top of that
live proof: rotated `orders`, `warehouse`, `payment`, `shipping`, and `support`
services; organic event-grown modules such as fraud screening and returns;
listener-based event repair; duplicate events; and malformed payloads from
external actors. It also emits `chaos-locustfile.py`, a Locust driver that can
send randomized valid and malformed fulfillment traffic against the running
REST proof services.

To run the generated services under Locust with 50 concurrent users:

```bash
make locust
```

The job starts auth, orders, warehouse, and shipping proof services, then drives
fulfillment, validation, quote, risk, event ingest/replay, return, support,
catalog recommendation, audit passport, and database status endpoints with
randomized traffic. The orders proof service persists CRUD rows, events,
passports, risks, returns, support tickets, and catalog data in a local SQLite
database under the generated `.modwire` directory.

To stress contract evolution and listener-based repair, run:

```bash
uv run python -B scripts/smoke_ecommerce_realm.py --force --contract-drift
```

The contract-drift smoke first generates the realm, then evolves the shipping
OpenAPI contract, regenerates shipping clients in the orders projects, attaches
a new shipping delivery listener, and reruns fulfillment through the evolved
client operation. The final confirmation must include `delivered_at`,
`carrier_tracking_url`, and `status: DELIVERED`. It also writes and executes
small generated-code smoke files for TypeScript and PHP, so the drift check
fails unless those generated shipping clients and listeners run successfully too.

## Contributing

Feature requests and bug reports are tracked through GitHub Issues:

- Open a feature request for architecture analyzers, output formats, or
  integrations.
- Open a bug report for incorrect architecture violations, graph output, shape
  reports, callable reports, unused export reports, packaging problems, or
  documentation mismatches.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the information to include and the
checks to run before opening a pull request.
