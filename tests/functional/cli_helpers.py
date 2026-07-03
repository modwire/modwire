import os
from pathlib import Path

from click.testing import Result
from click.testing import CliRunner

from modwire.cli import cli


def run_cli(args: list[str], cwd: Path) -> Result:
    previous_cwd = Path.cwd()
    runner = CliRunner()

    try:
        os.chdir(cwd)
        return runner.invoke(cli, args)
    finally:
        os.chdir(previous_cwd)
