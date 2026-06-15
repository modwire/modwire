# Large Project Fixtures

These fixtures are pinned e2e stress tests for the `enclosure` CLI running
against real large repositories.

Install the local package and `enclosure` CLI first:

```bash
python3 -m pip install -e .
python3 -m pip install "enclosure @ git+https://github.com/9orky/enclosure.git"
```

Run one fixture locally:

```bash
python3 tests/large_projects/run_large_project_fixtures.py --fixture django
```

Run all fixtures locally, continuing after failures and bounding each CLI
command:

```bash
python3 tests/large_projects/run_large_project_fixtures.py --keep-going
```

The default command timeout is 60 seconds. Use `--command-timeout 300` only for
an intentional long soak run.

The runner clones repositories into `.dev/large-projects`, writes each
project's `.enclosure/enclosure.yaml`, and runs the enclosure architecture
command suite from that project root. `PYTHONPATH` is set so a pipx-installed
`enclosure` uses this checkout's `src/modwire`.

The command suite intentionally allows normal violation exit codes for
commands that report policy failures, but still fails hard if the CLI emits
`Error:` or times out. That keeps the fixture useful as an e2e check instead
of hiding broken report paths.

For direct modwire debugging without the enclosure CLI:

```bash
python3 tests/large_projects/run_large_project_fixtures.py --fixture django --mode modwire
```

GitHub Actions runs the same runner from `.github/workflows/large-repo-fixtures.yml`.
It is manual and scheduled, with one matrix job per fixture so a slow or broken
legacy project does not block the rest of the fixture signal.
