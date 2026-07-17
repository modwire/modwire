# Architecture identity migration

Status: proposed for A1.1 owner acceptance

## Decision

The current Core library becomes the standalone Architecture library. Its
canonical identity is:

| Surface | Current identity | Target identity |
| --- | --- | --- |
| GitHub repository | `modwire/modwire` | `modwire/modwire-architecture` |
| PyPI distribution | `modwire` | `modwire-architecture` |
| Python import | `modwire` | `modwire_architecture` |
| Source root | `src/modwire` | `src/modwire_architecture` |
| First Architecture release | no release under the new identity | `1.0.0` |

This is a deliberate breaking migration. `modwire-architecture` is a new PyPI
distribution and starts its own semantic-version line at 1.0.0; the unreleased
`modwire` 5.0.0 line is not published as part of this migration.

GitHub's redirect from `modwire/modwire` is the only compatibility redirect.
There is no `modwire` PyPI wrapper and no `modwire` import shim. A wrapper
would preserve a misleading package identity, duplicate the public surface,
and make ownership of release and deprecation policy unclear.

## Consumer migration

Consumers move explicitly:

```bash
python -m pip uninstall modwire
python -m pip install modwire-architecture
```

```python
# Before
from modwire import ArchitectureConfig, Modwire

# After
from modwire_architecture import ArchitectureConfig, Modwire
```

Downstream packages must pin `modwire-architecture>=6,<7`, update imports, and
exercise their integration against a built wheel. In particular, the future
Modwire Agent is a consumer, not a compatibility layer for the old import.

## Release and rename sequence

1. Accept this policy before any identity change.
2. Prepare and merge A1.2: the distribution metadata, import tree, tests,
   manifests, documentation, links, and release configuration use the target
   identity, but no release is created.
3. The owner renames the GitHub repository to `modwire-architecture` after the
   A1.2 evidence confirms the old URL redirect and all repository references
   have an explicit target. The renamed repository remains the source for the
   same default branch and pull requests.
4. Update the `modwire-architecture` PyPI Trusted Publisher to the renamed
   repository and its repository-local release workflow. Verify this
   configuration before creating a release.
5. Complete A1.3 and A1.4, then use A1.5 to build, install, and test the
   release candidate. The first published GitHub Release and PyPI artifact are
   `v1.0.0` / `modwire-architecture==1.0.0`.

The `modwire` PyPI project remains a historical package. Its existing releases
are not deleted, republished, or altered.

## Rollback boundary

The owner invoking the GitHub repository rename is the first external,
potentially irreversible operation. Before that point, all work is ordinary
pull-request content and can be reverted without changing GitHub or PyPI.

After the rename, use a forward correction rather than assuming the old
repository name can be reclaimed. After PyPI publishes 1.0.0, do not attempt
to replace or delete the artifact; publish a corrective release instead.

## Affected implementation surfaces

A1.2 must update, at minimum:

- `pyproject.toml`, `uv.lock`, `MANIFEST.in`, package discovery, and generated
  version-file paths;
- `src/modwire`, all internal and external imports, tests, examples, and type
  marker placement;
- repository URLs, issue links, GitHub Actions release environment URLs, and
  PyPI Trusted Publishing configuration;
- contributor and migration documentation, including the precise installation
  and import transition above;
- the separately owned Ecosystem registry and the structural-change evidence
  bundle. This repository does not modify the Ecosystem repository itself.

No CLI behavior, local `.modwire` configuration, scan orchestration, Siren
capability behavior, Mermaid rendering, or ecosystem governance transfers as
part of this identity decision.
