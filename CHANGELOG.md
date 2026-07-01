# Changelog

## 3.0.0 - Unreleased

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
