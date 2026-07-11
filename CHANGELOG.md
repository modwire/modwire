# Changelog

## Unreleased

### Added

- Added a typed ecosystem dependency matrix with supported ranges and tested
  minimum versions.
- Added release trains as YAML with validated provider-before-consumer phases,
  gates, target dates, and GitHub Project field options.
- Added a contract-derived minimum/latest compatibility workflow and a
  repository-native release-train coordinator issue form.

### Changed

- Constrained Modwire building-block dependencies below their next unvalidated
  major versions.

## 4.0.2 - 2026-07-11

### Fixed

- Release asset uploads now target `GITHUB_REPOSITORY` explicitly when running
  from a reusable workflow without a repository checkout.

## 4.0.1 - 2026-07-11

### Changed

- GitHub Release publication now drives distribution building, asset
  attachment, and idempotent PyPI Trusted Publishing.

## 4.0.0 - 2026-07-11

### Breaking Changes

- Removed glossary and scaffolding from the `modwire` library surface.
- Moved the executable and Click runtime into the separate `modwire-cli` package.
- Removed runtime dependency injection; applications now use explicit standard factories.
- Raised the minimum Python version to 3.12 to align the ecosystem packages.

### Added

- Added `ModwireModel`, `ModwireConfigModel`, and `ModwireReportModel` as the
  common strict Pydantic taxonomy with JSON, YAML, dictionary, and file helpers.
- Added `Modwire`, a small façade coordinating extraction, architecture, Siren,
  and Mermaid packages.
- Added public layer, module, project, configuration, and report imports.
- Added the frozen GitHub ecosystem playbook, desired-state Project artifact,
  and reusable Python-package verification workflow.
- Added a typed, executable ecosystem source-of-truth contract with package
  taxonomy, CI validation, live GitHub drift detection, and reconciliation.
- Added the standard reusable Python verification, release-build, and GitHub
  Release workflows with a minimal repository-local PyPI publishing pattern.

### Changed

- `modwire` now composes `modwire-extraction`, `modwire-siren`, and
  `modwire-mermaid` as independently released building blocks.
- Architecture tag names and flow realm/analyzer names now reject duplicates.
- Packaging, tests, and releases no longer require a pre-existing `.dev`
  directory.

## 3.2.0

### Added

- Project generation through `modwire.projects.generate_project`.
- Bundled project profiles for Python/FastAPI/uv, TypeScript/NestJS/pnpm, and
  PHP/Symfony/Composer.
- Project authority loading and project-aware context/module operations through
  `modwire.projects.open_project`.
- Bundled `clean` and `ddd_context` module scaffoldings alongside the existing
  `layered` and `hexagonal` scaffoldings.
- Python, TypeScript, and PHP outputs for bundled DDD context module generation.
- `scripts/smoke_fleet.py`, which generates one three-service system across the
  bundled Python, TypeScript, and PHP profiles and returns per-service smoke
  responses.

### Changed

- README project-generation documentation now covers project-aware operations and
  the currently bundled project profiles.
- README development documentation now includes the smoke-fleet command.
- Python scaffold filenames now use snake_case names such as
  `accounts_repository.py` and `in_memory_accounts_repository.py`.
- Generated Python project and module scaffoldings no longer emit `__init__.py`
  marker files.

## 3.0.0

### Breaking Changes

- Replaced the previous function-style public API with an OOP-first architecture
  reporting API.
- Removed legacy helper entry points documented by older releases, including
  `evaluate_shape`, `render_callable_report`, `structured_callable_report`,
  `find_unused_exports`, `map_code`, `find_hotspots`, and `coherence_summary`.
- Consolidated architecture mapping, flow violations, shape violations, and
  insights into `ArchitectureReportRunner`.

### Added

- `ArchitectureReportRunner`, returning a typed `ArchitectureReport`.
- Normalized report sections for map data, violations, and insights.
- Public exports for the configuration objects needed to build reports from
  `modwire.architecture`.

### Migration

Use `ArchitectureReportRunner(config).run(code_map)` instead of calling
individual helper functions:

```python
from modwire.architecture import ArchitectureConfig, ArchitectureReportRunner

report = ArchitectureReportRunner(ArchitectureConfig(language="python")).run(code_map)
```
