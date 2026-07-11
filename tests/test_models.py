from pathlib import Path

import pytest
from pydantic import ValidationError

from modwire.code import CodePackage
from modwire.shared.config import BoundariesConfig, ModwireConfig, TagRule


def test_model_json_and_yaml_round_trips(tmp_path: Path) -> None:
    config = ModwireConfig(
        architecture={
            "boundaries": {
                "tags": [{"name": "module", "match": "src/*"}],
            }
        }
    )

    assert ModwireConfig.from_json(config.to_json()) == config
    assert ModwireConfig.from_yaml(config.to_yaml()) == config

    json_path = tmp_path / "config.json"
    yaml_path = tmp_path / "config.yaml"
    config.save_json(json_path)
    config.save_yaml(yaml_path)
    assert ModwireConfig.load_json(json_path) == config
    assert ModwireConfig.load_yaml(yaml_path) == config


def test_models_are_frozen_and_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ModwireConfig(unknown=True)

    config = ModwireConfig()
    with pytest.raises(ValidationError):
        config.projects = config.projects


def test_duplicate_architecture_tags_are_rejected() -> None:
    with pytest.raises(ValidationError, match="must be unique"):
        BoundariesConfig(
            tags=(
                TagRule(name="module", match="src/*"),
                TagRule(name="module", match="app/*"),
            )
        )


def test_code_package_validates_and_merges_paths() -> None:
    package = CodePackage(files={"src/domain/model.py": "class Model: ...\n"})
    merged = package.merged(CodePackage(files={"README.md": "# Example\n"}))

    assert merged.paths() == ("README.md", "src/domain/model.py")
    assert merged.contents_for("README.md") == "# Example\n"

    with pytest.raises(ValueError, match="duplicate paths"):
        package.merged(package)

    with pytest.raises(ValidationError, match="must be relative"):
        CodePackage(files={"/absolute.py": ""})
