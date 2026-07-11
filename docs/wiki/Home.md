# Modwire Wiki

Modwire coordinates typed architecture analysis over code maps produced by
`modwire-extraction`, with Siren and Mermaid integrations available through the
ecosystem façade.

## Start Here

- README describes the package boundaries, model taxonomy, ecosystem projects,
  and CLI split.
- [Reporting bugs](Reporting-bugs.md)
- [Requesting features](Requesting-features.md)
- [Development checks](Development-checks.md)

## Useful Project Links

- Repository: https://github.com/modwire/modwire
- Issues: https://github.com/modwire/modwire/issues
- Bug report form: https://github.com/modwire/modwire/issues/new?template=bug_report.yml
- Feature request form: https://github.com/modwire/modwire/issues/new?template=feature_request.yml

## Code Maps

Pass an already extracted `QueryableCodeMap` and an explicit
`ArchitectureConfig` to `Modwire().architecture(config).report(code_map)` or
`ArchitectureApplication.standard(config).report(code_map)`. Install the sibling
`modwire-cli` distribution for path discovery, configuration loading, generated
files, and terminal commands.
