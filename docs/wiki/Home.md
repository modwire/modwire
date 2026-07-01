# Modwire Wiki

Modwire maps architecture boundaries and evaluates policies from code maps
produced by `modwire-extraction`.

## Start Here

- README examples cover the OOP architecture report runner, including boundary
  maps, flow violations, shape violations, callable insights, hotspots, and
  unused export checks.
- [Reporting bugs](Reporting-bugs.md)
- [Requesting features](Requesting-features.md)
- [Development checks](Development-checks.md)

## Useful Project Links

- Repository: https://github.com/9orky/modwire
- Issues: https://github.com/9orky/modwire/issues
- Bug report form: https://github.com/9orky/modwire/issues/new?template=bug_report.yml
- Feature request form: https://github.com/9orky/modwire/issues/new?template=feature_request.yml

## Code Maps

Use `modwire-extraction` to produce `CodeMap` objects. Pass those maps into
`ArchitectureReportRunner` to produce a full architecture report.
