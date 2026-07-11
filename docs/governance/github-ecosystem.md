# Modwire GitHub Ecosystem Playbook

This document and [`.github/modwire-ecosystem.yml`](../../.github/modwire-ecosystem.yml)
are the frozen, repeatable definition of how the Modwire repositories are
coordinated on GitHub. The YAML file is the concise desired state; this document
explains how to apply and operate it.

## Source-of-truth boundary

For live GitHub work, use the connected GitHub app first. When the connector
does not expose a required capability, such as Projects v2 field management,
use `gh` in host mode. A live command is an application mechanism, never the
sole definition: represent every manageable GitHub detail in repository YAML,
workflow files, issue forms, or the reconciliation script before applying it.

`.github/modwire-ecosystem.yml` is the only source of truth for ecosystem
governance configuration. Its `packages` registry owns package identifiers,
repositories, distributions, Project components, roles, lifecycle, summaries,
and package dependencies. Repository links, the Project readme, and the
`Component` field options are derived from that registry and must not be
maintained as separate lists.

The same contract owns Project metadata and fields, saved-view definitions,
shared labels, automation policy, milestone policy, operating cadence, versioned
dependency edges, compatibility profiles, and named release trains. The
[dependency and release-train contract](dependencies-and-release-trains.md)
defines how those release controls are operated.
GitHub remains the source of truth for issue and pull-request content, status,
assignees, milestones, and discussion; copying delivery state into YAML would
create a conflicting tracker.

The contract is parsed by the strict Pydantic taxonomy in
`modwire.projects.ecosystem`. CI rejects unknown properties, duplicate package
identities, invalid field definitions, missing automation statuses, unknown or
cyclic dependencies, and malformed label colors. Run the same checks locally:

```bash
python .github/scripts/reconcile_ecosystem.py validate
python .github/scripts/reconcile_ecosystem.py check-live
```

`apply-live` converges Project metadata, repository links, shared labels, and
open issue/PR membership before checking for remaining drift:

```bash
python .github/scripts/reconcile_ecosystem.py apply-live
```

Saved views and built-in Project workflow configuration are represented in the
contract but currently require comparison and application in the GitHub UI;
GitHub does not expose those controls through `gh`. The drift report identifies
them explicitly as manual controls.

## Planning model

Use three levels of authority:

1. **Modwire Ecosystem Project** — the cross-repository roadmap, status,
   priority, risk, and release trains.
2. **`9orky/modwire` issues** — cross-package epics, architecture decisions,
   compatibility contracts, and integration release gates.
3. **Repository milestones** — delivery commitments owned by one package.

Do not copy another repository's issue into `modwire`. Create one coordinator
parent issue and attach the implementation issues from their owning
repositories as sub-issues. Versions remain independent; the Project's
`Release train` single-select options derive from the YAML contract and connect
compatible package milestones without forcing a shared version number.

The Project covers the coordinator (`modwire`), its runtime surface
(`modwire-cli`), the Extraction, Mermaid, and Siren building blocks, and the
in-progress MCP surface. Add a separately delivered package once, to the YAML
artifact's `packages` registry; repository membership and `Component` options
are derived from it.

## Bootstrap or restore the Project

1. Create a user-level Project owned by `9orky` named **Modwire Ecosystem**.
2. Set `9orky/modwire` as its default repository.
3. Link the Project from every repository derived from the package registry.
4. Create the custom fields and derived package/release-train options exactly as
   declared by the artifact.
5. Create the six saved views in the declared order.
6. Bulk-add all open issues and pull requests from every repository.
7. Enable the built-in added, closed, merged, and archive workflows.
8. Add one `is:open` auto-add workflow per repository where the GitHub plan's
   workflow limit permits it. If the limit is lower than the repository count,
   keep bulk addition as the fallback until Project GraphQL automation is
   justified.
9. Create the shared labels in each repository. Use Project fields for status,
   priority, horizon, and risk; use labels only for intrinsic issue properties
   and automation.
10. Publish the first Project status update with the current release train,
    risks, decisions needed, and next review date.

## Milestone policy

- A milestone belongs to exactly one repository and describes an outcome, not
  an ecosystem-wide version.
- Close a milestone as soon as all of its issues are closed. An open 100%
  milestone is stale planning state.
- Put unplanned work in the Project backlog instead of a permanent "Backlog"
  milestone.
- Use a coordinator parent issue for ecosystem work and attach package issues
  as cross-repository sub-issues.
- Assign the same Project `Release train` value to related milestones and
  issues, for example `2026-Q3 Contracts`.

## Issue placement

Create an issue in `modwire` when it changes at least two packages, defines an
ecosystem contract, records an architecture decision, or gates a coordinated
release. Create it in a member repository when that repository can deliver and
verify the result independently.

Every coordinator epic should state:

- the ecosystem outcome and compatibility promise;
- affected repositories;
- cross-repository sub-issues;
- release train and target date;
- integration verification required in `modwire`;
- rollout and rollback expectations.

## Workflow contract

The complete [Python workflow contract](python-workflows.md) defines the
coordinator's reusable CI, release-build, and release-assets workflows plus the
small repository-local entrypoints. Action versions, filenames, tag syntax,
artifact naming, and environment naming are part of the ecosystem SSOT.
Member repositories call a reviewed workflow-contract tag such as
`workflows-v1`, or a commit SHA for strict immutability.

The reusable workflow must always:

- test every supported Python version;
- run Ruff and the package's tests;
- build wheel and source distributions once on the oldest supported Python;
- validate distribution metadata;
- optionally upload verified artifacts.

Package release workflows remain local because publishing environments,
package names, and PyPI Trusted Publisher identities are repository-specific.
Only the credential-bearing PyPI job is local; build and GitHub Release asset
logic come from the coordinator's reusable workflows. Publishing a GitHub
Release is the event that drives PyPI publication. Releases must never require
a pre-existing `.dev` directory.

## Ecosystem integration gate

Keep an integration suite in `modwire` that installs the supported package
combination and exercises extraction, architecture reporting, Mermaid, Siren,
and eventually MCP scaffolding. Run it on pull requests, on a schedule, and
before a coordinator release. A package release may trigger it later through
`repository_dispatch`; scheduled execution is the lower-maintenance starting
point.

The `ecosystem-compatibility.yml` workflow provides minimum and latest profiles
for active consumers. Its matrix and Python versions are read from the
ecosystem contract; its required GitHub cron literal is drift-checked against
the same contract.

## Operating cadence

- Weekly: empty Inbox, assign priority/horizon, and resolve stale Blocked work.
- Monthly: review the roadmap and publish a Project status update.
- Before a package release: review its milestone and ecosystem release gates.
- After a release: close the milestone, update compatibility documentation,
  and archive completed Project items after 30 days.

## Current bootstrap actions

- Close the completed but still-open `modwire` milestones.
- Place `modwire` issues 13 and 14 in the next core milestone and release train.
- Create the initial `modwire-mcp` milestone described below.
- Keep the Project artifact updated whenever fields, views, repositories,
  labels, or cadence change. Changes to this artifact are governance changes
  and should be reviewed like public API changes.

### Initial `modwire-mcp` milestone

Title: **M1: Scaffolding Contract and MCP Transition**

Description:

> Stabilize the scaffolding server as the source of reusable ecosystem
> templates, align generated Python package workflows and metadata, expose the
> scaffolding contract through MCP, and preserve migration and verification
> coverage during the transition.

Suggested initial issues:

- Define the versioned scaffolding bundle and variable contract.
- Add the reusable Python-package workflow scaffolding.
- Make scaffolding synchronization idempotent and observable.
- Expose list, schema, bundle, and preview operations through MCP.
- Add end-to-end generation and clean-environment verification.
