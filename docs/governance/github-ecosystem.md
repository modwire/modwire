# Modwire GitHub Ecosystem Playbook

This document and [`.github/modwire-ecosystem.yml`](../../.github/modwire-ecosystem.yml)
are the frozen, repeatable definition of how the Modwire repositories are
coordinated on GitHub. The YAML file is the concise desired state; this document
explains how to apply and operate it.

## Source-of-truth boundary

`.github/modwire-ecosystem.yml` is the only source of truth for ecosystem
governance configuration. Its `packages` registry owns package identifiers,
repositories, distributions, Project components, roles, lifecycle, summaries,
and package dependencies. Repository links, the Project readme, and the
`Component` field options are derived from that registry and must not be
maintained as separate lists.

The same contract owns native organization issue types and issue fields,
Project metadata and workflow-only fields, saved-view definitions, shared
labels, relationship policy, issue intake, automation policy, milestone policy,
and operating cadence.
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

## Human merge approval

Every ecosystem repository protects its default branch with an active ruleset
named `Require human approval`. The ruleset requires the `Human approval`
status check produced by `.github/workflows/human-approval.yml`.

That workflow waits on the protected `human-approval` environment, where
`9orky` is the required reviewer. Every new pull-request commit cancels the
previous run and requires fresh approval. Agents must not approve or bypass this
environment. When the check is waiting, they must stop and ask the human reviewer
to use **Review deployments** before attempting the merge again.

## Planning model

Use three levels of authority:

1. **Modwire Ecosystem Project** — the cross-repository roadmap and workflow
   status. Durable planning facts are organization issue fields, so their values
   stay attached to an issue in every Project.
2. **`modwire/modwire` issues** — cross-package epics, architecture decisions,
   compatibility contracts, and integration release gates.
3. **Repository milestones** — delivery commitments owned by one package.

Do not copy another repository's issue into `modwire`. Create one coordinator
parent issue and attach the implementation issues from their owning
repositories as sub-issues. Versions remain independent; the Project's
`Release train` field connects compatible package milestones without forcing a
shared version number.

The Project covers the coordinator (`modwire`), its runtime surface
(`modwire-cli`), the Extraction, Mermaid, and Siren building blocks, and the
planned MCP integration. MCP remains incubating until CLI exposes the
filesystem, project, and execution capabilities it needs. The current local
Django scaffolding devserver is a prototype host, not a canonical Modwire
repository profile. Add a separately delivered package once, to the YAML
artifact's `packages` registry; repository membership and `Component` options
are derived from it.

## Bootstrap or restore the Project

1. Create an organization-level Project owned by `modwire` named **Modwire Ecosystem**.
2. Set `modwire/modwire` as its default repository.
3. Link the Project from every repository derived from the package registry.
4. Create the public organization issue fields and the Project-owned `Status`
   field exactly as declared by the artifact. Add the organization issue fields
   to the Project instead of creating duplicate Project-only fields.
5. Create the six saved views in the declared order.
6. Bulk-add all open issues and pull requests from every repository.
7. Enable the built-in added, closed, merged, and archive workflows.
8. Add one `is:open` auto-add workflow per repository where the GitHub plan's
   workflow limit permits it. If the limit is lower than the repository count,
   keep bulk addition as the fallback until Project GraphQL automation is
   justified.
9. Create the shared labels in each repository. Use the Project field only for
   workflow status, organization issue fields for structured issue facts, and
   labels only for orthogonal traits and automation.
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

## Native issue intake contract

Every agent-created issue must be complete when submitted. Human-created issues
may enter `Inbox` incomplete, but `needs-metadata` keeps them out of `Ready`
until the required values are present. Agents must ask for an uncertain value;
they must never invent priority, risk, horizon, effort, release placement, or a
relationship merely to satisfy validation.

Use GitHub's native organization issue types:

- `Bug` for incorrect existing behavior;
- `Feature` for new user-facing capability;
- `Task` for implementation, maintenance, documentation, and release work;
- `Epic` for a coordinated outcome delivered through native sub-issues;
- `Decision` for architecture, compatibility, and governance choices.

Issue forms set the native type and add the issue to `modwire/1`. Before
submission, populate every pinned required field: `Horizon`, `Priority`, `Risk`,
`Component`, `Release train`, and `Effort`. Use the explicit `Unscheduled`
value where planning or release placement has not been committed. `Start date`
and `Target date` are optional at intake and become meaningful once work is
scheduled. An assignee and objective acceptance criteria are required before
moving an issue to `Ready`.

The `Issue metadata` workflow checks the native type and organization field
values on creation and every relevant edit. It applies `needs-metadata`, leaves
an actionable checklist, and fails visibly while values are missing. It removes
the label after the issue is complete.

Use native relationships as the source of truth:

- `blocked by` and `blocking` for delivery dependencies;
- parent and sub-issues for hierarchy and epic progress;
- linked pull requests and linked branches for implementation;
- repository milestones for package release commitments.

Do not substitute `blocked` or `type:*` labels for native features. Labels are
reserved for independent facets such as `ecosystem`, `contract`, `breaking`,
`release-gate`, `documentation`, and `maintenance`.

The supported issue-creation operation is atomic: create the issue with its
native type, organization field values, labels, assignee and milestone, then
attach native parent/sub-issue and dependency relationships. The GitHub REST
and GraphQL APIs support this contract. Until the general GitHub connector
exposes every parameter, `modwire-mcp` is the integration boundary that must
provide the complete operation rather than falling back to an incomplete issue.

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

Title: **M1: CLI Capabilities and MCP Activation**

Description:

> Activate the MCP package after `modwire-cli` exposes stable filesystem,
> project, execution, and scaffolding capabilities. Keep the current Django
> scaffolding devserver as a development host until those capabilities can be
> composed through MCP without duplicating CLI behavior.

Suggested initial issues:

- Define the versioned CLI capability contract required by MCP.
- Expose filesystem, project, execution, and scaffolding operations through CLI.
- Make scaffolding synchronization idempotent and observable in the local devserver.
- Compose CLI capabilities into MCP list, schema, bundle, and preview operations.
- Add end-to-end generation and clean-environment verification.
