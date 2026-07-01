# Development Checks

Run these checks before opening a pull request:

```bash
uv run ruff check .
uv run --with pytest python -m pytest
uv run --with build python -m build --outdir dist
uv run --with twine python -m twine check dist/*
```

This page is the canonical local-check list; README and contributor guidance
link here to avoid release-process drift.

The CI workflow currently validates:

- Python 3.11, 3.12, and 3.13
- package build and distribution metadata
