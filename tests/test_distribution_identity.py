import tomllib
from importlib import import_module
from pathlib import Path

import pytest


def test_package_exposes_the_architecture_identity_only() -> None:
    package = import_module("modwire_architecture")

    assert package.__name__ == "modwire_architecture"
    with pytest.raises(ModuleNotFoundError):
        import_module("modwire")


def test_packaging_metadata_uses_the_architecture_distribution() -> None:
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    metadata = pyproject.read_text(encoding="utf-8")

    assert 'name = "modwire-architecture"' in metadata
    assert 'version_file = "src/modwire_architecture/_version.py"' in metadata


def test_extraction_is_the_only_direct_modwire_dependency() -> None:
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    modwire_dependencies = {
        dependency.split(">", 1)[0]
        for dependency in metadata["project"]["dependencies"]
        if dependency.startswith("modwire-")
    }

    assert modwire_dependencies == {"modwire-extraction"}
