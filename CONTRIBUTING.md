# Contributing to Modwire

Modwire is a Python package for extracting source-code dependencies and
evaluating architecture rules across Python, TypeScript/JavaScript, and PHP
projects.

## Requesting Features

Use the `Feature request` issue form for new capabilities, such as:

- support for another language or framework convention
- richer symbol, import, or graph metadata
- new architecture analyzers or policy matching behavior
- export formats or integrations with other tools
- documentation examples for common workflows

Feature requests are easiest to evaluate when they include the problem being
solved, a small example input, and the desired API or output shape.

## Reporting Bugs

Use the `Bug report` issue form for incorrect current behavior, such as:

- missing or incorrect imports, symbols, source IDs, or graph edges
- incorrect architecture-policy violations
- extractor crashes or runtime failures
- packaging, installation, or compatibility problems
- documentation that contradicts the implemented behavior

Bug reports should include a minimal reproduction, the expected output, the
actual output, and relevant versions for Python, Modwire, Node.js, or PHP.

## Pull Requests

Before opening a pull request, run the local checks:

```bash
uv run ruff check
uv run pytest
uv run python -m build --outdir dist
uv run twine check dist/*
```

Extractor changes should include focused tests under `tests/` and, when
relevant, a small fixture under `tests/apps/`.

Keep pull requests scoped to one behavior change. If an issue exists, link it in
the pull request description.
