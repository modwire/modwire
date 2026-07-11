# Python Workflow Contract

The Modwire ecosystem uses one workflow vocabulary and one release procedure.
The authoritative filenames, action versions, tag format, artifact name, and
PyPI environment are declared under `workflows` in
`.github/modwire-ecosystem.yml`.

## Standard workflow set

| File | Responsibility |
| --- | --- |
| `ci.yml` | Repository-local triggers and any package-specific supplemental checks. |
| `python-package.yml` | Reusable Python matrix tests, Ruff, build, Twine check, and optional artifact upload. |
| `release.yml` | Repository-local GitHub Release trigger and PyPI Trusted Publishing job. |
| `python-release-build.yml` | Reusable strict tag validation, clean SCM-derived build, Twine check, version check, and artifact upload. |
| `python-release-assets.yml` | Reusable attachment of verified distributions to the published GitHub Release. |

CI and release entrypoints are consistently named `ci.yml` and `release.yml`.
Reusable implementations are consistently prefixed with `python-`. Jobs use
the verbs `verify`, `build`, `publish-pypi`, and `publish-github-assets`.

## Release contract

1. Merge only after `ci.yml` passes.
2. Create and push a stable `vMAJOR.MINOR.PATCH` tag.
3. Publish a GitHub Release targeting that existing tag.
4. The `release.published` event passes the Release tag to the reusable build.
5. The build backend derives the version from the tag. Workflows never rewrite
   `pyproject.toml`, override setuptools-scm, or inspect wheels with embedded
   Python programs.
6. The reusable build creates one wheel and one source distribution, runs
   Twine, confirms both filenames contain the tag version, and uploads one
   immutable workflow artifact named `python-package-distributions`.
7. The reusable release-assets job attaches those distributions to the GitHub
   Release.
8. The repository-local `publish-pypi` job then downloads that artifact and
   uses PyPI Trusted Publishing with only `id-token: write`. Publication is
   idempotent so a rerun can recover a partial release without overwriting PyPI.

PyPI currently does not support Trusted Publishing from a reusable workflow.
Therefore the small `publish-pypi` job must remain directly in each
repository's `.github/workflows/release.yml`. Configure each PyPI project's
trusted publisher with that filename and the `pypi` environment.

## Member CI entrypoint

Member repositories call the coordinator workflow at the reviewed workflow
contract tag. Pinning a commit SHA is also allowed when stronger immutability is
needed.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  verify:
    uses: modwire/modwire/.github/workflows/python-package.yml@workflows-v1
    with:
      python-versions: '["3.12", "3.13", "3.14"]'
```

Package-specific checks belong in additional jobs in `ci.yml`. For example,
`modwire-extraction` keeps its Node and PHP conformance checks, while
`modwire-cli` may keep a coordinator integration job. Those jobs extend the
standard; they do not replace or copy it.

## Member release entrypoint

Every member `release.yml` has the same three jobs. Only the PyPI project URL
and, when necessary, reusable workflow inputs differ.

```yaml
name: Release

on:
  release:
    types: [published]

permissions:
  contents: read

jobs:
  build:
    uses: modwire/modwire/.github/workflows/python-release-build.yml@workflows-v1
    with:
      release-tag: ${{ github.event.release.tag_name }}

  publish-github-assets:
    needs: build
    uses: modwire/modwire/.github/workflows/python-release-assets.yml@workflows-v1
    with:
      release-tag: ${{ github.event.release.tag_name }}
    permissions:
      contents: write

  publish-pypi:
    needs: [build, publish-github-assets]
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/PACKAGE-NAME/
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v8
        with:
          name: python-package-distributions
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          skip-existing: true
```

## Updating the standard

Change action majors and workflow semantics first in the ecosystem contract,
then update the reusable implementations and tests in the same pull request.
Publish a new immutable workflow contract tag for breaking changes. Member
repositories adopt the new ref intentionally; they do not track `main`.
