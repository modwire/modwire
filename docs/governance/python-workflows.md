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
| `release.yml` | Repository-local stable-tag trigger and PyPI Trusted Publishing job. |
| `python-release-build.yml` | Reusable strict tag validation, clean SCM-derived build, Twine check, version check, and artifact upload. |
| `python-github-release.yml` | Reusable creation of the GitHub Release from the same verified artifacts. |

CI and release entrypoints are consistently named `ci.yml` and `release.yml`.
Reusable implementations are consistently prefixed with `python-`. Jobs use
the verbs `verify`, `build`, `publish-pypi`, and `publish-github`.

## Release contract

1. Merge only after `ci.yml` passes.
2. Create and push a stable `vMAJOR.MINOR.PATCH` tag.
3. `release.yml` passes that existing tag to the reusable release build.
4. The build backend derives the version from the tag. Workflows never rewrite
   `pyproject.toml`, override setuptools-scm, or inspect wheels with embedded
   Python programs.
5. The reusable build creates one wheel and one source distribution, runs
   Twine, confirms both filenames contain the tag version, and uploads one
   immutable workflow artifact named `python-package-distributions`.
6. The repository-local `publish-pypi` job downloads that artifact and uses
   PyPI Trusted Publishing with only `id-token: write`.
7. After PyPI succeeds, the reusable GitHub release job creates release notes
   and attaches the exact same distributions.

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
    uses: 9orky/modwire/.github/workflows/python-package.yml@workflows-v1
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
  push:
    tags: ["v*"]

permissions:
  contents: read

jobs:
  build:
    uses: 9orky/modwire/.github/workflows/python-release-build.yml@workflows-v1
    with:
      release-tag: ${{ github.ref_name }}

  publish-pypi:
    needs: build
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

  publish-github:
    needs: [build, publish-pypi]
    uses: 9orky/modwire/.github/workflows/python-github-release.yml@workflows-v1
    with:
      release-tag: ${{ github.ref_name }}
    permissions:
      contents: write
```

## Updating the standard

Change action majors and workflow semantics first in the ecosystem contract,
then update the reusable implementations and tests in the same pull request.
Publish a new immutable workflow contract tag for breaking changes. Member
repositories adopt the new ref intentionally; they do not track `main`.
