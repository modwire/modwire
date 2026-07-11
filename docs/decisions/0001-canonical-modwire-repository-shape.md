# Canonical Modwire Python repository and module shape

Status: accepted for contract version 1

## Decision

Every Modwire Python repository is created or adopted by two ordered scaffolds:

1. the UV package scaffold establishes Python packaging mechanics;
2. the Modwire repository scaffold declares ecosystem identity and module policy.

The Modwire scaffold is prototyped in the local Django scaffolding devserver.
That server is an implementation host, not a target repository kind and not
the operational `modwire-mcp` package. Core owns the versioned target contract
that the scaffold consumes. The scaffold never rewrites application code.

The machine-readable contract is
[`repository-contract-v1.yaml`](../scaffolding/repository-contract-v1.yaml).
Golden manifests define the supported initial shapes for a
[`library`](../scaffolding/golden/library.yaml) and
[`CLI`](../scaffolding/golden/cli.yaml) repository.

## Ecosystem audit

| Repository | Kind | Distribution | Import package | Source root | Current extension points |
| --- | --- | --- | --- | --- | --- |
| Core | library | `modwire` | `modwire` | `src` | architecture, projects, modules, layers |
| CLI | CLI | `modwire-cli` | `modwire_cli` | `src` | console entry point and command adapters |
| Extraction | library | `modwire-extraction` | `modwire_extraction` | `src` | code, dependency, extractors and bundled runtimes |
| Mermaid | library | `modwire-mermaid` | `modwire_mermaid` | `src` | diagram families, examples and generated API docs |
| Siren | library | `modwire-siren` | `modwire_siren` | `src` | contracts, policies, integrations and OpenAPI |

These five operational package repositories are the scaffold targets. The
incubating `modwire-mcp` package is not a third target shape: it becomes
workable after `modwire-cli` provides its filesystem, project, execution, and
scaffolding capabilities. The current local Django devserver is not included
in this audit.

Common invariants are deliberately small: a UV-managed Python project, a
stable repository/distribution/import identity, an explicit source root,
declared modules and exclusions, deterministic Modwire configuration, tests,
and a reserved `shared` module. Feature names, internal layers, entry points,
framework files, examples, generated runtimes and documentation layouts remain
repository-specific.

Repositories that do not yet contain a `shared` module are valid adoption
inputs. Preview proposes creating the empty foundation; apply never moves code
into it.

## Module contract

- `shared` is reserved and has no module dependencies.
- Feature modules may depend on `shared` and on explicitly listed feature
  modules only.
- Every dependency target must be declared; self-dependencies and cycles are
  invalid.
- A module may choose its own internal layers. The repository contract does
  not prescribe one package's layers for another package.
- Package `__init__.py` files are export surfaces. Construction and application
  logic live in normal modules, including dedicated composition modules.
- Exclusions describe generated, vendored, migration, fixture or development
  paths and are repository-specific.

## Ownership and collisions

UV exclusively owns packaging mechanics: `pyproject.toml`, `uv.lock`, the
Python version selection, build metadata and the initial import package.
Modwire does not patch these files.

Modwire exclusively owns `.modwire/repository.yaml`. It creates default
`.modwire/shape.yaml` and `.modwire/boundaries.yaml` only when absent. Existing
shape and boundary policy is preserved because it may contain deliberate
repository-specific rules.

For new module directories, Modwire may create only missing directories and
empty export-only `__init__.py` files. Any existing source file is preserved.
If a requested generated path is occupied by content with another owner,
preview reports a conflict and apply stops atomically. No "best effort" partial
write is allowed.

## Preview, idempotency and adoption

Preview is mandatory and side-effect free. It returns a stable, path-sorted
plan with `create`, `replace`, `unchanged`, `preserve`, or `conflict` for every
managed path, plus the expected hash of each write. Apply accepts that preview
identity and refuses stale plans.

Applying the same variables twice produces no writes on the second run.
Rendering is byte-stable: UTF-8, LF newlines, one final newline, stable key
ordering and no timestamps or random identifiers.

Adoption inventories the existing repository before rendering. It validates
UV prerequisites and identity, preserves all application files, imports
existing Modwire policy as authoritative extension data, proposes only missing
managed files, and reports incompatible identity or collisions without
writing. Existing repositories are never normalized by moving or renaming
their code.

## Consequences

The local scaffolding devserver can expose a HATEOAS workflow with separate
discover, preview and apply actions while Core remains filesystem-independent.
The future `modwire-mcp` package will compose the stable capabilities supplied
by `modwire-cli`; it does not inherit the devserver's Django repository shape.
Contract version 1 can be implemented without deciding repository-specific
architecture layers or rewriting any target repository.
