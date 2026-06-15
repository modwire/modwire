# Development Checks

Run these checks before opening a pull request:

```bash
uv run ruff check
uv run pytest
uv run python -m build --outdir dist
uv run twine check dist/*
```

This page is the canonical local-check list; README and contributor guidance
link here to avoid release-process drift.

Extractor changes should include focused tests under `tests/` and, when useful,
small source fixtures under `tests/apps/`.

The CI workflow currently validates:

- Python 3.11, 3.12, and 3.13
- Node.js syntax for the TypeScript/JavaScript extractor helper
- PHP syntax for the PHP extractor helper
- package build and distribution metadata
