# Changelog

## 3.2.0 - Unreleased

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
