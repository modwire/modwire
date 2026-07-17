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
