import pytest
from pydantic import ValidationError

from modwire_architecture.code import CodePackage
from modwire_architecture.shared.config import BoundariesConfig, ModwireConfig, ShapeConfig, TagRule


def test_model_json_and_yaml_round_trips() -> None:
    config = ModwireConfig(
        architecture={
            "boundaries": {
                "tags": [{"name": "module", "match": "src/*"}],
            }
        }
    )

    assert ModwireConfig.from_json(config.to_json()) == config
    assert ModwireConfig.from_yaml(config.to_yaml()) == config

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


def test_shape_defaults_allow_module_and_symbol_imports() -> None:
    config = ShapeConfig()

    assert config.require_joined_imports is True
    assert config.allowed_import_crossing_types == ("module", "symbol")


def test_code_package_validates_and_merges_paths() -> None:
    package = CodePackage(files={"src/domain/model.py": "class Model: ...\n"})
    merged = package.merged(CodePackage(files={"README.md": "# Example\n"}))

    assert merged.paths() == ("README.md", "src/domain/model.py")
    assert merged.contents_for("README.md") == "# Example\n"

    with pytest.raises(ValueError, match="duplicate paths"):
        package.merged(package)

    with pytest.raises(ValidationError, match="must be relative"):
        CodePackage(files={"/absolute.py": ""})
