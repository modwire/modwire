# Contributing to Modwire

Modwire is a Python package for architecture mapping, violation evaluation, and
code-map reports produced from `modwire-extraction` data. The library also
coordinates `modwire-siren` and `modwire-mermaid`; terminal behavior belongs in
the sibling `modwire-cli` project.

## Requesting Features

Use the `Feature request` issue form for new capabilities, such as:

- architecture mapping for another framework convention
- richer architecture analysis, shape reports, callable reports, or export checks
- new architecture analyzers or policy matching behavior
- export formats or integrations with other tools
- documentation examples for common workflows

Feature requests are easiest to evaluate when they include the problem being
solved, a small example input, and the desired API or output shape.

## Reporting Bugs

Use the `Bug report` issue form for incorrect current behavior, such as:

- incorrect architecture-policy violations
- incorrect shape, callable, unused-export, or graph reports
- packaging, installation, or compatibility problems
- documentation that contradicts the implemented behavior

Bug reports should include a minimal reproduction, the expected output, the
actual output, and relevant versions for Python, Modwire, and modwire-extraction.

## Pull Requests

Before opening a pull request, run the local checks documented in
[Development checks](docs/wiki/Development-checks.md).

Keep pull requests scoped to one behavior change. If an issue exists, link it in
the pull request description.
