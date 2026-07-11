# Dependency Matrix and Release Trains

The executable definitions live in
[`.github/modwire-ecosystem.yml`](../../.github/modwire-ecosystem.yml). This
document explains the policy; it must not become a second registry of package
constraints, train names, phase membership, dates, or gates.

## Dependency contract

Each package-to-package edge declares two values:

- `specifier` is the supported PEP 440 range that belongs in the consumer's
  package metadata. The next unvalidated major version is excluded.
- `minimum` is the oldest supported version. It must also be the lower bound in
  `specifier` and is continuously exercised for active consumers.

The package graph, Project component list, compatibility matrix, and release
ordering are all derived from the package registry. Leaf packages have an empty
dependency mapping. A dependency change is made in a pull request against the
consumer and must update its package metadata, lock file, tests, and ecosystem
contract together.

The current graph is:

```text
Extraction ──┬──> Core ──> CLI
Mermaid ─────┤
Siren ───────┘
Extraction ─────> MCP
```

Versions remain independent. A provider's patch or minor release is compatible
when it remains inside the declared consumer range. A provider major is not
adopted by widening a range speculatively: it requires a coordinated release
train and evidence from both compatibility profiles.

## Compatibility profiles

`minimum` installs the exact lower-bound versions on the oldest ecosystem
Python version. `latest` lets the resolver choose the newest versions inside
the declared ranges on the newest ecosystem Python version. Normal CI still
tests every supported Python version.

The `Ecosystem compatibility` GitHub Actions workflow generates its active
consumer matrix at runtime from the YAML contract. It runs on relevant pull
requests, every Monday at the declared and drift-checked cron schedule, and on
manual dispatch. Incubating packages join this gate when their lifecycle moves
to `active`. A scheduled failure means the declared range is no longer truthful
and blocks release readiness until the consumer is fixed or its range is
narrowed.

## Release train contract

A release train coordinates compatibility, not version numbers. Each named
train declares a status, an optional target date, ordered phases, and required gates. The
Project `Release train` single-select options are derived from those names, so
issues and pull requests cannot silently create a second naming scheme.

Phases are topologically validated: a provider in the train must appear before
each consumer. For the active contracts train, building blocks move first, the
coordinator follows, and runtime/integration surfaces move last. A package may
skip publication when it has no change, but its phase gate must still be
reviewed.

For each train:

1. Open one coordinator issue in `9orky/modwire` with the YAML issue form.
2. Add repository-owned implementation issues as cross-repository sub-issues.
3. Assign the same Project release-train option and target date to every item.
4. Prepare providers and validate consumer candidates before publishing.
5. Publish packages in phase order only after package CI, minimum, latest, and
   release-readiness gates pass.
6. Stop the train on an incompatible artifact. Do not widen a range or skip a
   gate after publication; fix forward with a patch or yank the bad package.
7. Complete the coordinator issue, close package milestones, and retain the
   train definition as release history.

Package releases continue to use repository-local GitHub Releases and PyPI
Trusted Publishers. Release-train state belongs in the ecosystem YAML and
GitHub Project fields; no external tracker is authoritative.

## Changing the contract

A dependency or train change is a governance change. Review the YAML, generated
matrix, consumer metadata, and workflow behavior in one pull request, then run:

```bash
python .github/scripts/reconcile_ecosystem.py validate
python .github/scripts/reconcile_ecosystem.py github-matrix
python .github/scripts/reconcile_ecosystem.py check-live
```

When changing the live Project field from free text to contract-derived options,
run `migrate-release-train-field`. It preserves populated values, refuses to
drop unknown train names, verifies the copied assignments, and only then removes
the legacy field.

Use `apply-live` only after review to converge controls that the GitHub CLI can
manage. Saved views and built-in Project workflows remain manual controls until
GitHub exposes configuration APIs for them.
